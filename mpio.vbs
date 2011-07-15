Set objWMIService = GetObject("winmgmts:root\wmi")

For Count=0 to Wscript.Arguments(0)
    Set GetDescriptor = objWMIService.ExecQuery("SELECT * FROM MPIO_GET_DESCRIPTOR")
    Set LBPolicy = objWmiService.ExecQuery("SELECT * FROM DSM_QueryLBPolicy_V2")
Next
