param(
    [Parameter(Mandatory=$true)]
    [string]$Email,
    
    [Parameter(Mandatory=$true)]
    [string]$AppPassword
)

# Gmail IMAP search via raw .NET TLS sockets
$imapServer = "imap.gmail.com"
$imapPort = 993
$tagCounter = 1

function Send-ImapCommand {
    param([System.IO.StreamWriter]$writer, [System.IO.StreamReader]$reader, [string]$command, [switch]$hideCommand)
    
    $tag = "A$($script:tagCounter)"
    $script:tagCounter++
    $fullCommand = "$tag $command"
    
    if (-not $hideCommand) {
        Write-Host ">> $fullCommand" -ForegroundColor DarkGray
    } else {
        Write-Host ">> $tag LOGIN ****" -ForegroundColor DarkGray
    }
    
    $writer.WriteLine($fullCommand)
    $writer.Flush()
    
    $response = @()
    while ($true) {
        $line = $reader.ReadLine()
        if ($null -eq $line) { break }
        $response += $line
        Write-Host "<< $line" -ForegroundColor DarkGray
        if ($line.StartsWith("$tag ")) { break }
    }
    return $response
}

function Fetch-MessageHeaders {
    param(
        [System.IO.StreamWriter]$writer,
        [System.IO.StreamReader]$reader,
        [string]$uid
    )
    
    $tag = "A$($script:tagCounter)"
    $script:tagCounter++
    $fullCommand = "$tag UID FETCH $uid (BODY.PEEK[HEADER.FIELDS (FROM SUBJECT DATE)])"
    
    $writer.WriteLine($fullCommand)
    $writer.Flush()
    
    $headerLines = @()
    while ($true) {
        $line = $reader.ReadLine()
        if ($null -eq $line) { break }
        $headerLines += $line
        if ($line.StartsWith("$tag ")) { break }
    }
    return $headerLines
}

try {
    Write-Host "`n=== Searching Gmail: $Email ===" -ForegroundColor Cyan
    Write-Host "Connecting to $imapServer`:$imapPort..." -ForegroundColor Yellow
    
    # Connect via TLS
    $tcpClient = New-Object System.Net.Sockets.TcpClient($imapServer, $imapPort)
    $sslStream = New-Object System.Net.Security.SslStream($tcpClient.GetStream(), $false)
    $sslStream.AuthenticateAsClient($imapServer)
    
    $reader = New-Object System.IO.StreamReader($sslStream)
    $writer = New-Object System.IO.StreamWriter($sslStream)
    $writer.AutoFlush = $false
    
    # Read greeting
    $greeting = $reader.ReadLine()
    Write-Host "<< $greeting" -ForegroundColor DarkGray
    
    # Login
    $loginResp = Send-ImapCommand -writer $writer -reader $reader -command "LOGIN `"$Email`" `"$AppPassword`"" -hideCommand
    if ($loginResp[-1] -notmatch "OK") {
        Write-Host "LOGIN FAILED: $($loginResp[-1])" -ForegroundColor Red
        return
    }
    Write-Host "Logged in successfully!" -ForegroundColor Green
    
    # Select All Mail to search everything
    $selectResp = Send-ImapCommand -writer $writer -reader $reader -command 'SELECT "[Gmail]/All Mail"'
    if ($selectResp[-1] -notmatch "OK") {
        # Try alternative folder name (localized Gmail)
        $selectResp = Send-ImapCommand -writer $writer -reader $reader -command 'SELECT "[Gmail]/Tous les messages"'
        if ($selectResp[-1] -notmatch "OK") {
            # Fallback to INBOX
            $selectResp = Send-ImapCommand -writer $writer -reader $reader -command 'SELECT INBOX'
        }
    }
    
    # Search queries - looking for Adobe Sign / e-sign from a broker
    $searches = @(
        'SUBJECT "adobe sign"',
        'SUBJECT "Adobe Acrobat Sign"',
        'SUBJECT "echosign"',
        'SUBJECT "signature"',
        'FROM "adobesign"',
        'FROM "echosign"',
        'FROM "courtier"',
        'SUBJECT "courtier"',
        'SUBJECT "mandat"',
        'SUBJECT "procuration"',
        'SUBJECT "compromis"',
        'SUBJECT "immobilier"',
        'FROM "notaire"',
        'SUBJECT "broker"'
    )
    
    $allUids = @{}
    
    foreach ($query in $searches) {
        $searchResp = Send-ImapCommand -writer $writer -reader $reader -command "UID SEARCH $query"
        foreach ($line in $searchResp) {
            if ($line -match "^\* SEARCH(.*)") {
                $uids = $Matches[1].Trim() -split '\s+' | Where-Object { $_ -ne '' }
                if ($uids.Count -gt 0) {
                    Write-Host "  Found $($uids.Count) result(s) for: $query" -ForegroundColor Green
                    foreach ($uid in $uids) {
                        $allUids[$uid] = $query
                    }
                }
            }
        }
    }
    
    if ($allUids.Count -eq 0) {
        Write-Host "`nNo matching emails found." -ForegroundColor Yellow
    } else {
        Write-Host "`n=== Found $($allUids.Count) unique matching email(s) ===" -ForegroundColor Cyan
        
        # Fetch headers for each unique UID (limit to most recent 30)
        $sortedUids = $allUids.Keys | Sort-Object { [int]$_ } -Descending | Select-Object -First 30
        
        foreach ($uid in $sortedUids) {
            Write-Host "`n--- UID: $uid (matched: $($allUids[$uid])) ---" -ForegroundColor Magenta
            $headers = Fetch-MessageHeaders -writer $writer -reader $reader -uid $uid
            foreach ($line in $headers) {
                if ($line -match "^(From|Subject|Date):") {
                    Write-Host "  $line" -ForegroundColor White
                }
            }
        }
    }
    
    # Logout
    Send-ImapCommand -writer $writer -reader $reader -command "LOGOUT" | Out-Null
    
} catch {
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
} finally {
    if ($reader) { $reader.Dispose() }
    if ($writer) { $writer.Dispose() }
    if ($sslStream) { $sslStream.Dispose() }
    if ($tcpClient) { $tcpClient.Dispose() }
}
