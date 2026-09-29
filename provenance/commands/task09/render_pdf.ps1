# Render a DOCX to PDF with Microsoft Word (COM), the render tool available on this host.
# Alerts are disabled so no hidden dialog can block; the Word instance is always closed.
# Usage: powershell -File render_pdf.ps1 <docx> <pdf>
param([Parameter(Mandatory = $true)][string]$Docx, [Parameter(Mandatory = $true)][string]$Pdf)
$ErrorActionPreference = 'Stop'
$word = New-Object -ComObject Word.Application
$word.Visible = $false
$word.DisplayAlerts = 0
try {
    # Open(FileName, ConfirmConversions, ReadOnly, AddToRecentFiles)
    $doc = $word.Documents.Open($Docx, $false, $true, $false)
    $doc.SaveAs2($Pdf, 17)
    $pages = $doc.ComputeStatistics(2)
    $doc.Close($false)
    Write-Output "word=$($word.Version) pages=$pages pdf=$Pdf"
}
finally {
    $word.Quit()
    [System.Runtime.InteropServices.Marshal]::ReleaseComObject($word) | Out-Null
}
