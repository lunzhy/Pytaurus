proj_load "%plt%" PLT
cv_createDS IV "PLT gate2 InnerVoltage" "PLT drain TotalCurrent"
cv_createWithFormula IdVg "log10(<IV>)"  A A A A
set Id %vth.current%
set Vth	[cv_compute "vecvalx(<IdVg>,log10($Id))" A A A A ]
ft_scalar Vth [format %.3f $Vth]