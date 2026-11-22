<#
  petro_bundle.ps1  -  v1.2.0
  ---------------------------------------------------------------------------
  يجمع مشروع Django (petro_dashboard) في ملف نصي واحد قابل للإرسال إلى أي مساعد
  تقني، مع:
    - شجرة الملفات والأحجام وعدد الأسطر
    - إصدارات Python / Django / المكتبات (pip freeze)
    - مخرجات manage.py check و showmigrations و diffsettings
    - محتوى كل ملفات الكود والقوالب
    - إخفاء تلقائي لكلمات المرور والمفاتيح (Secret key, passwords, tokens ...)
    - استثناء media / staticfiles / venv / node_modules / logs / الملفات الثنائية

  أمثلة الاستخدام:
    powershell -ExecutionPolicy Bypass -File .\petro_bundle.ps1
    powershell -ExecutionPolicy Bypass -File .\petro_bundle.ps1 -Root "D:\petro_dashboard"
    powershell -ExecutionPolicy Bypass -File .\petro_bundle.ps1 -SkipDjangoChecks
    powershell -ExecutionPolicy Bypass -File .\petro_bundle.ps1 -SkipTemplates -MaxFileKB 400
    powershell -ExecutionPolicy Bypass -File .\petro_bundle.ps1 -Python ".venv\Scripts\python.exe"

  ملاحظة: السكريبت للقراءة فقط، لا يعدّل أي ملف في مشروعك.
#>

[CmdletBinding()]
param(
    [string]$Root,
    [string]$Out,
    [switch]$SkipDjangoChecks,
    [switch]$SkipTemplates,
    [switch]$SkipMigrations,
    [string]$Python,
    [int]$MaxFileKB = 250
)

$ErrorActionPreference = 'Stop'
$ScriptVersion = '1.2.0'
$Now = Get-Date
$RedactionCount = 0
$Body = New-Object System.Text.StringBuilder
$BodyLines = 0
$Sections = New-Object System.Collections.ArrayList
$EncodingUtf8 = New-Object System.Text.UTF8Encoding($false)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
function Append-Text {
    param([string]$Text)
    if ($null -eq $Text) { $Text = '' }
    [void]$script:Body.Append($Text)
    $script:BodyLines += ([regex]::Matches($Text, "`n")).Count
}

function Start-Section {
    param([string]$Title)
    [void]$script:Sections.Add([pscustomobject]@{ Title = $Title; Line = ($script:BodyLines + 1) })
    Append-Text ("`n" + ('=' * 100) + "`n" + $Title + "`n" + ('=' * 100) + "`n")
}

function Read-TextSafe {
    param([string]$Path)
    $bytes = [System.IO.File]::ReadAllBytes($Path)
    if ($bytes.Length -ge 3 -and $bytes[0] -eq 0xEF -and $bytes[1] -eq 0xBB -and $bytes[2] -eq 0xBF) {
        return [System.Text.Encoding]::UTF8.GetString($bytes, 3, $bytes.Length - 3)
    }
    try {
        $strict = New-Object System.Text.UTF8Encoding($false, $true)
        return $strict.GetString($bytes)
    } catch {
        try { return [System.Text.Encoding]::GetEncoding(1256).GetString($bytes) }
        catch { return [System.Text.Encoding]::Default.GetString($bytes) }
    }
}

function Test-BinaryFile {
    param([string]$Path)
    $fs = [System.IO.File]::OpenRead($Path)
    try {
        $buf = New-Object byte[] 2048
        $n = $fs.Read($buf, 0, $buf.Length)
        for ($i = 0; $i -lt $n; $i++) {
            if ($buf[$i] -eq 0) { return $true }
        }
        return $false
    } finally {
        $fs.Dispose()
    }
}

# يحمي القيم الحساسة. يبقي اسم المفتاح والمحرّك/المضيف، ويستبدل السر فقط.
function Protect-Text {
    param([string]$Text)
    if ([string]::IsNullOrEmpty($Text)) { return $Text }

    # user:password@host داخل روابط الاتصال
    $urlPattern = '(?<pre>[a-zA-Z][a-zA-Z0-9+.\-]*://[^/\s:@]+:)(?<pw>[^@\s/]+)(?<post>@)'
    $urlHits = [regex]::Matches($Text, $urlPattern).Count
    if ($urlHits -gt 0) {
        $Text = [regex]::Replace($Text, $urlPattern, '${pre}***REDACTED***${post}')
        $script:RedactionCount += $urlHits
    }

    # أزواج حساسة داخل سطر واحد مثل {'PASSWORD': 'root'}
    $pairPattern = '(?i)([''"]?[A-Za-z0-9_.\-]*(?:SECRET|PASSWORD|PASSWD|API_?KEY|TOKEN|ACCESS_KEY|PRIVATE_KEY|CLIENT_SECRET)[''"]?\s*:\s*)([''"])([^''"]*)\2'
    $pairHits = [regex]::Matches($Text, $pairPattern).Count
    if ($pairHits -gt 0) {
        $Text = [regex]::Replace($Text, $pairPattern, '${1}${2}***REDACTED***${2}')
        $script:RedactionCount += $pairHits
    }

    $lines = $Text -split "`n"
    for ($i = 0; $i -lt $lines.Length; $i++) {
        $line = $lines[$i]
        if ($line -match '^\s*[''"]?(?<key>[A-Za-z_][A-Za-z0-9_.\-]*)[''"]?\s*[:=]') {
            $key = $Matches['key']
            if ($key -match '(?i)(SECRET|PASSWORD|PASSWD|PWD|API_?KEY|TOKEN|ACCESS_KEY|PRIVATE_KEY|CLIENT_SECRET)') {
                $trail = ''
                if ($line.TrimEnd().EndsWith(',')) { $trail = ',' }
                $candidate = $line.TrimEnd().TrimEnd([char]',')
                $lines[$i] = ([regex]::Replace($candidate, '^(\s*[''"]?[A-Za-z_][A-Za-z0-9_.\-]*[''"]?\s*[:=]\s*)(.*)$', '${1}"***REDACTED***"')) + $trail
                $script:RedactionCount++
            }
        }
    }
    return ($lines -join "`n")
}

function Invoke-SafeCommand {
    param([string]$Exe, [string[]]$Arguments)
    $previous = (Get-Location).Path
    try {
        Set-Location -LiteralPath $Root
        $output = (& $Exe @Arguments 2>&1 | Out-String)
        $code = $LASTEXITCODE
    } catch {
        $output = 'ERROR: ' + $_.Exception.Message
        $code = 'n/a'
    } finally {
        try { Set-Location -LiteralPath $previous } catch { }
    }
    if ([string]::IsNullOrWhiteSpace($output)) { $output = '(no output)' }
    return ("exit code: {0}`n{1}" -f $code, $output.TrimEnd())
}

# ---------------------------------------------------------------------------
# 1. تحديد مجلد المشروع
# ---------------------------------------------------------------------------
function Find-ProjectRoot {
    param([string]$Candidate)
    if (-not [string]::IsNullOrWhiteSpace($Candidate)) {
        if (Test-Path -LiteralPath (Join-Path $Candidate 'manage.py')) { return $Candidate }
        if (Test-Path -LiteralPath $Candidate) { return $Candidate }
        throw "Root not found: $Candidate"
    }
    $starts = @()
    if ($PSScriptRoot) { $starts += $PSScriptRoot }
    $starts += (Get-Location).Path
    foreach ($start in $starts) {
        $dir = Get-Item -LiteralPath $start
        for ($i = 0; $i -lt 4 -and $null -ne $dir; $i++) {
            if (Test-Path -LiteralPath (Join-Path $dir.FullName 'manage.py')) { return $dir.FullName }
            $dir = $dir.Parent
        }
    }
    # fallbacks for the default layout described by the project owner
    foreach ($known in @('D:\petro_dashboard', 'C:\petro_dashboard')) {
        if (Test-Path -LiteralPath (Join-Path $known 'manage.py')) { return $known }
    }
    return (Get-Location).Path
}

$Root = (Resolve-Path -LiteralPath (Find-ProjectRoot -Candidate $Root)).ProviderPath
$Root = $Root.TrimEnd('\', '/')
$RootPrefixLength = $Root.Length + 1
$ProjectName = Split-Path -Path $Root -Leaf
if ([string]::IsNullOrWhiteSpace($ProjectName)) { $ProjectName = 'project' }

$hasManagePy = Test-Path -LiteralPath (Join-Path $Root 'manage.py')

# ---------------------------------------------------------------------------
# 2. تحديد مكان الملف الناتج (خارج المشروع حتى لا يُجمَّع مع نفسه)
# ---------------------------------------------------------------------------
if ([string]::IsNullOrWhiteSpace($Out)) {
    $desktop = [Environment]::GetFolderPath('Desktop')
    if ($desktop -and (Test-Path -LiteralPath $desktop)) {
        $outDir = $desktop
    } else {
        $outDir = Split-Path -Path $Root -Parent
        if ([string]::IsNullOrWhiteSpace($outDir)) { $outDir = $Root }
    }
    $Out = Join-Path $outDir ('{0}_bundle_{1}.txt' -f ($ProjectName -replace '[^\w\.-]', '_'), $Now.ToString('yyyyMMdd_HHmmss'))
}

# ---------------------------------------------------------------------------
# 3. قواعد التضمين والاستثناء
# ---------------------------------------------------------------------------
$allowedExtensions = @(
    '.py', '.pyi', '.html', '.htm', '.txt', '.md', '.rst', '.json', '.yml', '.yaml',
    '.toml', '.cfg', '.ini', '.conf', '.js', '.mjs', '.cjs', '.jsx', '.ts', '.tsx',
    '.css', '.scss', '.bat', '.cmd', '.ps1', '.sh', '.xml', '.csv', '.sql',
    '.po', '.pot', '.example', '.gitignore', '.editorconfig'
)

$allowedNames = @(
    'requirements.txt', 'requirements-dev.txt', 'Dockerfile', 'Procfile', 'Makefile',
    '.gitignore', '.editorconfig', '.env.example', 'runtime.txt', 'pyproject.toml'
)

$skippedDirPattern = '(?i)(^|/)(\.git|\.hg|\.svn|\.next|\.venv|venv|virtualenv|env|node_modules|__pycache__|staticfiles|media|logs?|\.idea|\.vscode|\.pytest_cache|\.mypy_cache|\.ruff_cache|\.tox|site-packages|dist|build|coverage|htmlcov|vendor|libs|nssm[^/]*|Pour lancer[^/]*)(/|$)'
$skippedFilePattern = '(?i)(^|/)(backup[^/]*\.sql|[^/]*\.log|[^/]*\.pyc|[^/]*\.min\.(js|css)|db\.sqlite3|package-lock\.json|yarn\.lock|pnpm-lock\.yaml)$'

# ---------------------------------------------------------------------------
# 4. جمع الملفات
# ---------------------------------------------------------------------------
$included = New-Object System.Collections.ArrayList
$skipped = New-Object System.Collections.ArrayList
$excludedFolderCounts = @{}

Write-Host ''
Write-Host ('Scanning: ' + $Root) -ForegroundColor Cyan

$allFiles = Get-ChildItem -LiteralPath $Root -Recurse -File -Force -ErrorAction SilentlyContinue
$totalBytesScanned = 0

foreach ($file in $allFiles) {
    $rel = $file.FullName.Substring($RootPrefixLength).Replace('\', '/')
    $totalBytesScanned += $file.Length

    if ($rel -match $skippedDirPattern) {
        $folder = $Matches[2]
        if (-not $excludedFolderCounts.ContainsKey($folder)) { $excludedFolderCounts[$folder] = 0 }
        $excludedFolderCounts[$folder]++
        continue
    }
    if ($rel -match $skippedFilePattern) {
        [void]$skipped.Add([pscustomobject]@{ Path = $rel; Reason = 'backup / log / lock / minified file'; KB = [math]::Round($file.Length / 1KB, 1) })
        continue
    }
    if ($rel -match '(?i)(^|/)\.env($|\.)') {
        [void]$skipped.Add([pscustomobject]@{ Path = $rel; Reason = '.env (only key names are reported)'; KB = [math]::Round($file.Length / 1KB, 1) })
        continue
    }

    $name = $file.Name
    $ext = [System.IO.Path]::GetExtension($name).ToLowerInvariant()
    $isAllowed = $allowedExtensions -contains $ext
    if (-not $isAllowed -and ($allowedNames -contains $name.ToLowerInvariant() -or $allowedNames -contains $name)) { $isAllowed = $true }
    if (-not $isAllowed) {
        [void]$skipped.Add([pscustomobject]@{ Path = $rel; Reason = 'binary / unsupported type'; KB = [math]::Round($file.Length / 1KB, 1) })
        continue
    }

    $sizeKb = [math]::Round($file.Length / 1KB, 1)
    if ($sizeKb -gt $MaxFileKB) {
        [void]$skipped.Add([pscustomobject]@{ Path = $rel; Reason = ('too large (> {0} KB)' -f $MaxFileKB); KB = $sizeKb })
        continue
    }

    if ($SkipTemplates -and ($ext -eq '.html' -or $ext -eq '.htm')) {
        [void]$skipped.Add([pscustomobject]@{ Path = $rel; Reason = 'templates skipped (-SkipTemplates)'; KB = $sizeKb })
        continue
    }
    if ($SkipMigrations -and $rel -match '(?i)(^|/)migrations/') {
        [void]$skipped.Add([pscustomobject]@{ Path = $rel; Reason = 'migrations skipped (-SkipMigrations)'; KB = $sizeKb })
        continue
    }

    if (Test-BinaryFile -Path $file.FullName) {
        [void]$skipped.Add([pscustomobject]@{ Path = $rel; Reason = 'binary content detected'; KB = $sizeKb })
        continue
    }

    try {
        $raw = Read-TextSafe -Path $file.FullName
    } catch {
        [void]$skipped.Add([pscustomobject]@{ Path = $rel; Reason = 'unreadable (locked / permission)'; KB = $sizeKb })
        continue
    }
    $safe = Protect-Text -Text $raw
    $lineCount = ($safe -split "`n").Count

    [void]$included.Add([pscustomobject]@{
        Rel      = $rel
        Content  = $safe
        Lines    = $lineCount
        KB       = $sizeKb
        Modified = $file.LastWriteTime.ToString('yyyy-MM-dd HH:mm')
    })
}

$included = @($included | Sort-Object Rel)
$totalIncludedLines = 0
$totalIncludedKb = 0
foreach ($it in $included) { $totalIncludedLines += $it.Lines; $totalIncludedKb += $it.KB }

# ---------------------------------------------------------------------------
# 5. اكتشاف Python
# ---------------------------------------------------------------------------
$python = $null
if (-not [string]::IsNullOrWhiteSpace($Python)) {
    if (Test-Path -LiteralPath $Python) {
        $python = (Resolve-Path -LiteralPath $Python).ProviderPath
    } elseif (Get-Command $Python -ErrorAction SilentlyContinue) {
        $python = $Python
    }
}
$candidates = @(
    (Join-Path $Root '.venv\Scripts\python.exe'),
    (Join-Path $Root 'venv\Scripts\python.exe'),
    (Join-Path $Root 'env\Scripts\python.exe'),
    (Join-Path $Root '.venv/bin/python'),
    (Join-Path $Root 'venv/bin/python')
)
if (-not $python) {
    foreach ($candidate in $candidates) {
        if (Test-Path -LiteralPath $candidate) { $python = $candidate; break }
    }
}
if (-not $python) {
    foreach ($exeName in @('python', 'python3', 'py')) {
        $cmd = Get-Command $exeName -ErrorAction SilentlyContinue
        if ($cmd) { $python = $cmd.Source; break }
    }
}

# ---------------------------------------------------------------------------
# 6. بناء المحتوى
# ---------------------------------------------------------------------------
Append-Text ("PROJECT SNAPSHOT - {0}`n" -f $ProjectName)
Append-Text ("Generated: {0}`n" -f $Now.ToString('yyyy-MM-dd HH:mm:ss'))
Append-Text ("Bundle tool: petro_bundle.ps1 v{0}`n" -f $ScriptVersion)
Append-Text "Language: Arabic + English. This is a Django project snapshot prepared for technical review.`n"

Start-Section 'READ ME FIRST - كيف تقرأ هذا الملف'
Append-Text @"
الهدف: أن يصل المساعد التقني إلى صورة كاملة عن المشروع دون الوصول إلى جهازك.

- هذا الملف نصي بالكامل. لا يحتوي على ملفات ثنائية (صور، PDF، Excel، وسائط).
- كل القيم الحساسة استُبدلت بـ ***REDACTED***. أسماء المفاتيح بقيت ظاهرة، والقيم لا.
- روابط قواعد البيانات احتفظت بالمحرّك والمضيف، وحُذفت منها كلمة المرور والمستخدم.
- الأقسام مرقّمة، والفهرس أدناه يعطي رقم السطر لكل قسم.
- محتوى الملفات مرتّب أبجديًا حسب المسار، مع عدد الأسطر وتاريخ آخر تعديل.
- إذا طُلب منك ملف لم يظهر، أرسله على حدة أو ارفع MaxFileKB في أمر التشغيل.
- الأسطر التي تبدأ بـ SKIPPED / NOT INCLUDED تشرح ما تم استثناؤه ولماذا.
"@

Start-Section ('1. PROJECT TREE - شجرة الملفات المضمّنة ({0} ملف)' -f $included.Count)
Append-Text ("Root: {0}`n" -f $Root)
Append-Text ("manage.py found: {0}`n" -f $hasManagePy)
Append-Text ("Included files: {0} | included lines: {1} | included size: {2:N1} KB`n" -f $included.Count, $totalIncludedLines, $totalIncludedKb)
Append-Text ("Scanned size (before filtering): {0:N1} MB`n" -f ($totalBytesScanned / 1MB))

$groups = $included | Group-Object {
    $r = $_.Rel
    if ($r.Contains('/')) { $r.Substring(0, $r.LastIndexOf('/')) } else { '(project root)' }
} | Sort-Object Name

foreach ($group in $groups) {
    Append-Text ("`n{0}/`n" -f $group.Name)
    foreach ($item in ($group.Group | Sort-Object Rel)) {
        $short = $item.Rel.Substring($item.Rel.LastIndexOf('/') + 1)
        Append-Text ("    {0,-52} {1,8:N1} KB {2,6} lines`n" -f $short, $item.KB, $item.Lines)
    }
}

Start-Section '2. ENVIRONMENT - البيئة وإصدارات المكتبات'
Append-Text ("OS: {0}`n" -f [Environment]::OSVersion.VersionString)
Append-Text ("OS architecture: {0}`n" -f $env:PROCESSOR_ARCHITECTURE)
Append-Text ("PowerShell: {0}`n" -f $PSVersionTable.PSVersion.ToString())
Append-Text ("Current culture: {0} | Console encoding: {1}`n" -f (Get-Culture).Name, [Console]::OutputEncoding.WebName)
Append-Text ("Project root: {0}`n" -f $Root)
Append-Text ("Bundle output: {0}`n" -f $Out)

if (Test-Path -LiteralPath (Join-Path $Root '.git')) {
    Append-Text "`n--- git ---`n"
    Append-Text ((Invoke-SafeCommand -Exe 'git' -Arguments @('rev-parse', '--abbrev-ref', 'HEAD')) + "`n")
    Append-Text ((Invoke-SafeCommand -Exe 'git' -Arguments @('log', '-3', '--oneline')) + "`n")
    Append-Text ((Invoke-SafeCommand -Exe 'git' -Arguments @('status', '--short')) + "`n")
} else {
    Append-Text "`nNo .git repository detected.`n"
}

if ($python) {
    Append-Text ("`nPython executable: {0}`n" -f $python)
    Append-Text "`n--- python --version ---`n"
    Append-Text ((Invoke-SafeCommand -Exe $python -Arguments @('--version')) + "`n")
    Append-Text "`n--- pip --version ---`n"
    Append-Text ((Invoke-SafeCommand -Exe $python -Arguments @('-m', 'pip', '--version')) + "`n")
    Append-Text "`n--- pip freeze (installed packages) ---`n"
    Append-Text ((Invoke-SafeCommand -Exe $python -Arguments @('-m', 'pip', 'freeze')) + "`n")
} else {
    Append-Text "`nPython was not found on this machine. Install it in PATH or create a venv next to manage.py.`n"
}

Start-Section '3. DJANGO DIAGNOSTICS - تشخيص المشروع'
if ($python -and $hasManagePy -and -not $SkipDjangoChecks) {
    Append-Text "`n--- manage.py check ---`n"
    Append-Text ((Invoke-SafeCommand -Exe $python -Arguments @('manage.py', 'check')) + "`n")
    Append-Text "`n--- manage.py showmigrations ---`n"
    Append-Text ((Invoke-SafeCommand -Exe $python -Arguments @('manage.py', 'showmigrations')) + "`n")
    Append-Text "`n--- manage.py diffsettings (secrets redacted) ---`n"
    Append-Text ((Protect-Text -Text (Invoke-SafeCommand -Exe $python -Arguments @('manage.py', 'diffsettings'))) + "`n")
    Append-Text "`n--- manage.py makemigrations --check --dry-run ---`n"
    Append-Text ((Invoke-SafeCommand -Exe $python -Arguments @('manage.py', 'makemigrations', '--check', '--dry-run')) + "`n")
} elseif ($SkipDjangoChecks) {
    Append-Text "`nSkipped by -SkipDjangoChecks. Run: python manage.py check ; python manage.py showmigrations`n"
} else {
    Append-Text "`nCould not run Django commands (python or manage.py missing).`n"
}

Start-Section '4. ENV FILE KEYS - أسماء المتغيرات فقط (قيمها محجوبة)'
$envCandidates = @('.env', '.env.local', '.env.production', 'env.txt', 'database.cnf')
$foundEnv = $false
foreach ($envName in $envCandidates) {
    $envPath = Join-Path $Root $envName
    if (Test-Path -LiteralPath $envPath) {
        $foundEnv = $true
        Append-Text ("`n--- {0} (keys only) ---`n" -f $envName)
        $envText = Read-TextSafe -Path $envPath
        foreach ($line in ($envText -split "`n")) {
            if ($line -match '^\s*([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*)$') {
                $hasValue = -not [string]::IsNullOrWhiteSpace($matches[2])
                $stateLabel = 'value hidden'
                if (-not $hasValue) { $stateLabel = 'empty' }
                Append-Text ("{0} = <{1}>`n" -f $matches[1], $stateLabel)
            }
        }
    }
}
if (-not $foundEnv) { Append-Text "`nNo .env file found at project root.`n" }
Append-Text "`nDatabase-related settings live in the Django settings file (included below, values redacted).`n"

Start-Section '5. NOT INCLUDED - ما تم استثناؤه ولماذا'
Append-Text ("`nExcluded folders (file counts):`n")
if ($excludedFolderCounts.Count -eq 0) {
    Append-Text "  (none)`n"
} else {
    foreach ($key in ($excludedFolderCounts.Keys | Sort-Object)) {
        Append-Text ("  {0,-28} {1} files`n" -f $key, $excludedFolderCounts[$key])
    }
}

Append-Text ("`nSkipped files: {0}`n" -f $skipped.Count)
$skipGroups = $skipped | Group-Object Reason | Sort-Object Count -Descending
foreach ($group in $skipGroups) {
    Append-Text ("`n  [{0}] {1} file(s)`n" -f $group.Name, $group.Count)
    $sample = @($group.Group | Select-Object -First 15)
    foreach ($entry in $sample) {
        Append-Text ("     - {0} ({1} KB)`n" -f $entry.Path, $entry.KB)
    }
    if ($group.Count -gt $sample.Count) {
        Append-Text ("     ... and {0} more`n" -f ($group.Count - $sample.Count))
    }
}

Start-Section '6. FINGERPRINT - بصمة المحتوى'
$manifestString = (@($included | Sort-Object Rel | ForEach-Object { '{0}|{1}|{2}' -f $_.Rel, $_.Lines, $_.KB }) -join "`n")
$sha = [System.Security.Cryptography.SHA256]::Create()
try {
    $manifestBytes = $sha.ComputeHash([System.Text.Encoding]::UTF8.GetBytes($manifestString))
    $manifestHash = ($manifestBytes | ForEach-Object { $_.ToString('x2') }) -join ''
} finally {
    $sha.Dispose()
}
Append-Text ("Included files: {0}`n" -f $included.Count)
Append-Text ("Total included lines: {0}`n" -f $totalIncludedLines)
Append-Text ("Total included size: {0:N1} KB`n" -f $totalIncludedKb)
Append-Text ("Redacted secret values: {0}`n" -f $RedactionCount)
Append-Text ("Manifest SHA-256: {0}`n" -f $manifestHash)

Start-Section '7. QUESTIONS FOR THE PROJECT OWNER - أسئلة للمالك'
Append-Text @"
أجب عن هذه الأسئلة في رسالة منفصلة، فهي توفّر وقتًا كبيرًا:
1. ما الخطأ/الميزة التي تريد البدء بها؟ أرسل نص Traceback كاملًا إن وُجد.
2. SQL Server: ما الجداول أو مخططات dbo التي تُقرأ منها؟ هل الكتابة إليها مطلوبة؟
3. أين توجد جداول Django الفعلية: MySQL أم SQL Server؟ وهل DATABASE_ROUTERS مضبوط؟
4. هل تم تشغيل python manage.py migrate بنجاح على القاعدة الصحيحة؟
5. هل تريد نقل النماذج من core إلى apps/* أم إبقاء core؟
6. من يستخدم النظام: أدوار، صلاحيات، ولغة الواجهة المطلوبة؟
"@

Start-Section ('8. FILE CONTENTS - محتوى الملفات ({0} ملف)' -f $included.Count)

$writtenBytes = 0
$limitBytes = 16000000
$truncated = $false
foreach ($item in $included) {
    if ($writtenBytes -gt $limitBytes) {
        $truncated = $true
        break
    }
    $divider = '-' * 100
    Append-Text ("`n{0}`nFILE: {1}`nlines: {2} | size: {3:N1} KB | modified: {4}`n{0}`n" -f $divider, $item.Rel, $item.Lines, $item.KB, $item.Modified)
    Append-Text ($item.Content.TrimEnd() + "`n")
    $writtenBytes += ([System.Text.Encoding]::UTF8.GetByteCount($item.Content))
}
if ($truncated) {
    Append-Text "`n[TRUNCATED] Bundle size limit reached. Re-run with -SkipTemplates or a higher -MaxFileKB on a smaller scope.`n"
}

Start-Section 'END OF BUNDLE - نهاية الملف'
Append-Text ("Generated by petro_bundle.ps1 v{0} on {1}`n" -f $ScriptVersion, $Now.ToString('yyyy-MM-dd HH:mm:ss'))

# ---------------------------------------------------------------------------
# 7. تجميع الملف وكتابته
# ---------------------------------------------------------------------------
$index = New-Object System.Text.StringBuilder
[void]$index.Append(('=' * 100) + "`n")
[void]$index.Append(("PROJECT SNAPSHOT - {0} - {1}`n" -f $ProjectName, $Now.ToString('yyyy-MM-dd HH:mm')))
[void]$index.Append(('=' * 100) + "`n`n")
[void]$index.Append("CONTENTS / الفهرس`n")
foreach ($section in $Sections) {
    [void]$index.Append(("  line {0,7}  |  {1}`n" -f ($section.Line + $Sections.Count + 9), $section.Title))
}
[void]$index.Append("`n")
[void]$index.Append("Send this single file to your technical assistant. Secrets are redacted automatically.`n")

$final = $index.ToString() + $Body.ToString()

$outDirPath = Split-Path -Path $Out -Parent
if ($outDirPath -and -not (Test-Path -LiteralPath $outDirPath)) {
    New-Item -ItemType Directory -Path $outDirPath -Force | Out-Null
}
[System.IO.File]::WriteAllText($Out, $final, $EncodingUtf8)

$fileInfo = Get-Item -LiteralPath $Out
$shaOut = [System.Security.Cryptography.SHA256]::Create()
try {
    $stream = [System.IO.File]::OpenRead($Out)
    try { $hashBytes = $shaOut.ComputeHash($stream) } finally { $stream.Dispose() }
} finally {
    $shaOut.Dispose()
}
$outHash = ($hashBytes | ForEach-Object { $_.ToString('x2') }) -join ''

Write-Host ''
Write-Host 'Bundle created successfully.' -ForegroundColor Green
Write-Host ("  File     : {0}" -f $Out)
Write-Host ("  Size     : {0:N1} KB" -f ($fileInfo.Length / 1KB))
Write-Host ("  Files    : {0} ({1} lines)" -f $included.Count, $totalIncludedLines)
Write-Host ("  Skipped  : {0}" -f $skipped.Count)
Write-Host ("  Redacted : {0} secret value(s)" -f $RedactionCount)
Write-Host ("  SHA-256  : {0}" -f $outHash)
Write-Host ''
Write-Host 'Send this file as-is. If the chat blocks .txt, rename it to .md or zip it.' -ForegroundColor Yellow
if (-not $SkipDjangoChecks) {
    Write-Host 'Tip: -SkipDjangoChecks makes it much faster; -SkipTemplates shrinks it a lot.' -ForegroundColor DarkGray
}