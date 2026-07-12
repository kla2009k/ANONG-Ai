param(
    [string]$DocxPath = "",
    [string]$PdfPath = ""
)

$projectRoot = Split-Path -Parent $PSScriptRoot
if (-not $DocxPath) {
    $DocxPath = Join-Path $projectRoot "docs\wseec_2026\CerviCo_Pilot_WSEEC_2026_Full_Paper_Polished.docx"
}
if (-not $PdfPath) {
    $PdfPath = Join-Path $projectRoot "docs\wseec_2026\CerviCo_Pilot_WSEEC_2026_Full_Paper_Polished.pdf"
}

$word = New-Object -ComObject Word.Application
$word.Visible = $false
$word.DisplayAlerts = 0
try {
    $doc = $word.Documents.Open($DocxPath, $false, $false)
    $doc.Repaginate()
    $pages = $doc.ComputeStatistics(2)
    if ($pages -ne 12) {
        throw "Expected exactly 12 Word pages, found $pages. Adjust the builder before export."
    }
    $wdExportFormatPDF = 17
    $doc.ExportAsFixedFormat($PdfPath, $wdExportFormatPDF)
    $doc.Close($false)
    Write-Output "word_pages=$pages"
    Write-Output "pdf=$PdfPath"
}
finally {
    $word.Quit()
}
