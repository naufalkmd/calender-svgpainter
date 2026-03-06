param(
    [string]$CanvasPath = (Join-Path (Split-Path $PSScriptRoot -Parent) "painter/canvas.json"),
    [string]$PreviewOutputPath = (Join-Path (Split-Path $PSScriptRoot -Parent) "Assets/github-painter-preview.svg"),
    [string]$ExportOutputPath = (Join-Path (Split-Path $PSScriptRoot -Parent) "Assets/github-painter-banner.svg"),
    [int]$CellSize = 30,
    [int]$Gap = 2,
    [int]$PreviewPadding = 8,
    [int]$ExportPadding = 6
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$previewBackground = "#0f0f0f"
$previewInactive = "#262626"
$activePalette = @{
    "1" = "#0d4429"
    "2" = "#016c31"
    "3" = "#26a641"
    "4" = "#39d353"
}

$canvas = Get-Content $CanvasPath -Raw | ConvertFrom-Json
$rowCount = if ($canvas.rows) { [int]$canvas.rows } else { 7 }
$columnCount = if ($canvas.columns) { [int]$canvas.columns } else { 53 }

if ($rowCount -ne 7 -or $columnCount -ne 53) {
    throw "painter/canvas.json must define a 53x7 board."
}

$rows = New-Object System.Collections.Generic.List[string]
foreach ($sourceRow in @($canvas.grid | Select-Object -First $rowCount)) {
    $safeRow = ([string]$sourceRow).Replace(" ", ".") -replace '[^\.1234]', '.'
    if ($safeRow.Length -gt $columnCount) {
        $safeRow = $safeRow.Substring(0, $columnCount)
    }
    elseif ($safeRow.Length -lt $columnCount) {
        $safeRow = $safeRow.PadRight($columnCount, ".")
    }
    $rows.Add($safeRow)
}

while ($rows.Count -lt $rowCount) {
    $rows.Add(("." * $columnCount))
}

$step = $CellSize + $Gap

function New-Svg {
    param(
        [string]$OutputPath,
        [int]$Padding,
        [bool]$Transparent
    )

    $activeCells = New-Object System.Collections.Generic.List[object]
    for ($rowIndex = 0; $rowIndex -lt $rowCount; $rowIndex++) {
        $row = $rows[$rowIndex]
        for ($columnIndex = 0; $columnIndex -lt $columnCount; $columnIndex++) {
            $symbol = [string]$row[$columnIndex]
            if ($symbol -eq ".") {
                continue
            }

            $activeCells.Add([PSCustomObject]@{
                Column = $columnIndex
                Row = $rowIndex
                Symbol = $symbol
            })
        }
    }

    if ($Transparent -and $activeCells.Count -eq 0) {
        throw "Transparent export cannot be generated from a fully empty canvas."
    }

    if ($Transparent) {
        $minColumn = ($activeCells.Column | Measure-Object -Minimum).Minimum
        $maxColumn = ($activeCells.Column | Measure-Object -Maximum).Maximum
        $minRow = ($activeCells.Row | Measure-Object -Minimum).Minimum
        $maxRow = ($activeCells.Row | Measure-Object -Maximum).Maximum
    }
    else {
        $minColumn = 0
        $maxColumn = $columnCount - 1
        $minRow = 0
        $maxRow = $rowCount - 1
    }

    $renderColumns = $maxColumn - $minColumn + 1
    $renderRows = $maxRow - $minRow + 1
    $width = ($renderColumns * $step) - $Gap + (2 * $Padding)
    $height = ($renderRows * $step) - $Gap + (2 * $Padding)

    $svg = [System.Text.StringBuilder]::new()
    [void]$svg.AppendLine('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ' + $width + ' ' + $height + '" role="img" aria-labelledby="title desc">')
    [void]$svg.AppendLine('  <title id="title">GitHub Painter Canvas Render</title>')
    [void]$svg.AppendLine('  <desc id="desc">Generated from painter/canvas.json.</desc>')

    if (-not $Transparent) {
        [void]$svg.AppendLine('  <rect width="' + $width + '" height="' + $height + '" fill="' + $previewBackground + '"/>')
    }

    for ($rowIndex = $minRow; $rowIndex -le $maxRow; $rowIndex++) {
        $row = $rows[$rowIndex]
        for ($columnIndex = $minColumn; $columnIndex -le $maxColumn; $columnIndex++) {
            $symbol = [string]$row[$columnIndex]
            $x = $Padding + (($columnIndex - $minColumn) * $step)
            $y = $Padding + (($rowIndex - $minRow) * $step)

            if ($symbol -eq ".") {
                if (-not $Transparent) {
                    [void]$svg.AppendLine('  <rect x="' + $x + '" y="' + $y + '" width="' + $CellSize + '" height="' + $CellSize + '" rx="4" fill="' + $previewInactive + '"/>')
                }
                continue
            }

            [void]$svg.AppendLine('  <rect x="' + $x + '" y="' + $y + '" width="' + $CellSize + '" height="' + $CellSize + '" rx="4" fill="' + $activePalette[$symbol] + '"/>')
        }
    }

    [void]$svg.AppendLine('</svg>')

    $outputDirectory = Split-Path $OutputPath -Parent
    if ($outputDirectory -and -not (Test-Path $outputDirectory)) {
        New-Item -ItemType Directory -Path $outputDirectory | Out-Null
    }

    [System.IO.File]::WriteAllText($OutputPath, $svg.ToString(), [System.Text.UTF8Encoding]::new($false))
    Write-Host "Wrote $OutputPath"
}

New-Svg -OutputPath $PreviewOutputPath -Padding $PreviewPadding -Transparent:$false
New-Svg -OutputPath $ExportOutputPath -Padding $ExportPadding -Transparent:$true
