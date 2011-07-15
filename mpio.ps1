$start = get-date
for ($i=0;$i -le 2000; $i++) {

$mpio = Get-WmiObject -namespace "root\wmi" -query "SELECT * FROM MPIO_GET_DESCRIPTOR"
$second = Get-WmiObject -namespace "root\wmi" -query "SELECT * FROM DSM_QueryLBPolicy_V2"
}
$end = get-date

$result = New-TimeSpan $start $end
write-host $result