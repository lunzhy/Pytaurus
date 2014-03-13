;In this file, all the stack region under isolations and gates can be split into grids (in annotation).
;Percentage symbol is used to indicate that current line should be substitute

;rX -- right x coordinate
;lX -- left x coordinate
;tY -- top y coordinate
;bY -- bottom y coordinate

;parameters from user input, thickness and length values are in [nm]
(define ThicknessGate %tc.iso.thick%)               ;(define ThicknessGate 10)
(define ThicknessStack %tc.stack.thick%)            ;(define ThicknessStack 5)
(define ThicknessSubstrate 80)
(define LengthGate1 %tc.gate1.width%)               ;(define LengthGate1 45)
(define LengthIsolation2 %tc.iso2.width%)           ;(define LengthIsolation2 30)
(define LengthGate2 %tc.gate2.width%)               ;(define LengthGate2 45)
(define LengthIsolation3 %tc.iso3.width%)           ;(define LengthIsolation3 30)
(define LengthGate3 %tc.gate3.width%)               ;(define LengthGate3 45)
(define LengthIsolation1 LengthIsolation2)          ;(define LengthIsolation1 30)
(define LengthIsolation4 LengthIsolation3)          ;(define LengthIsolation4 30)
(define SubstrateDoping 5e18)
(define JunctionDepth 45)
(define ChannelDepth 15)

<end>

;variables used in this command file
(define Nsubs SubstrateDoping)
(define JDepth (* 1e-3 JunctionDepth))
(define ChDepth (* 1e-3 ChannelDepth))

(define Tgate (* 1e-3 ThicknessGate))
(define Tstack (* 1e-3 ThicknessStack))
(define Tsubs (* 1e-3 ThicknessSubstrate))
(define Liso1 (* 1e-3 LengthIsolation1))
(define Lgate1 (* 1e-3 LengthGate1))
(define Liso2 (* 1e-3 LengthIsolation2))
(define Lgate2 (* 1e-3 LengthGate2))
(define Liso3 (* 1e-3 LengthIsolation3))
(define Lgate3 (* 1e-3 LengthGate3))
(define Liso4 (* 1e-3 LengthIsolation4))

(define X_zero 0)
(define Y_zero 0)

(define lX_subs X_zero)
(define tY_subs Y_zero)
(define bY_subs (- tY_subs Tsubs))

(define lX_stack lX_subs)
(define bY_stack tY_subs)
(define tY_stack (+ bY_stack Tstack))

(define tY_gate (+ tY_stack Tgate))

(define lX_i1 lX_stack);left x coordinate of isolation 1
(define rX_i1 (+ lX_stack Liso1))
(define rX_g1 (+ rX_i1 Lgate1))
(define rX_i2 (+ rX_g1 Liso2))
(define rX_g2 (+ rX_i2 Lgate2))
(define rX_i3 (+ rX_g2 Liso3))
(define rX_g3 (+ rX_i3 Lgate3))
(define rX_i4 (+ rX_g3 Liso4))

(define rX_subs rX_i4)

;create substrate
(sdegeo:create-rectangle (position lX_stack bY_stack 0) (position rX_subs bY_subs 0) "Silicon" "R.subs")

;create gate stack layer, 3 stack regions under each isolation or gate region
;;create regions under isolation 1
;(define lX_section lX_stack) ;left x coordinate of this section, under isolation 1
;(define Lgrid (/ Liso1 3))
;(define rX_r1 (+ lX_section Lgrid)) ;region 1
;(define rX_r2 (+ rX_r1 Lgrid)) ;region 2
;(define rX_r3 (+ rX_r2 Lgrid)) ;region 3
;(sdegeo:create-rectangle (position lX_section bY_stack 0) (position rX_r1 tY_stack 0) "SiO2" "R.iso1.gr1")
;(sdegeo:create-rectangle (position rX_r1 bY_stack 0) (position rX_r2 tY_stack 0) "SiO2" "R.iso1.gr2")
;(sdegeo:create-rectangle (position rX_r2 bY_stack 0) (position rX_r3 tY_stack 0) "SiO2" "R.iso1.gr3")
(sdegeo:create-rectangle (position lX_i1 bY_stack 0) (position rX_i1 tY_stack 0) "SiO2" "R.iso1.stack")

<end>

;;create regions under gate 1
(define lX_section rX_i1)
(define Lgrid (/ Lgate1 3))
(define rX_r1 (+ lX_section Lgrid)) ;region 1
(define rX_r2 (+ rX_r1 Lgrid)) ;region 2
(define rX_r3 (+ rX_r2 Lgrid)) ;region 3
(sdegeo:create-rectangle (position lX_section bY_stack 0) (position rX_r1 tY_stack 0) "SiO2" "R.gate1.gr1")
(sdegeo:create-rectangle (position rX_r1 bY_stack 0) (position rX_r2 tY_stack 0) "SiO2" "R.gate1.gr2")
(sdegeo:create-rectangle (position rX_r2 bY_stack 0) (position rX_r3 tY_stack 0) "SiO2" "R.gate1.gr3")

;;create regions under isolation 2
(define lX_section rX_g1)
(define Lgrid (/ Liso2 3))
(define rX_r1 (+ lX_section Lgrid)) ;region 1
(define rX_r2 (+ rX_r1 Lgrid)) ;region 2
(define rX_r3 (+ rX_r2 Lgrid)) ;region 3
(sdegeo:create-rectangle (position lX_section bY_stack 0) (position rX_r1 tY_stack 0) "SiO2" "R.iso2.gr1")
(sdegeo:create-rectangle (position rX_r1 bY_stack 0) (position rX_r2 tY_stack 0) "SiO2" "R.iso2.gr2")
(sdegeo:create-rectangle (position rX_r2 bY_stack 0) (position rX_r3 tY_stack 0) "SiO2" "R.iso2.gr3")


;;create regions under gate 2
(define lX_section rX_i2)
(define Lgrid (/ Lgate2 3))
(define rX_r1 (+ lX_section Lgrid)) ;region 1
(define rX_r2 (+ rX_r1 Lgrid)) ;region 2
(define rX_r3 (+ rX_r2 Lgrid)) ;region 3
(sdegeo:create-rectangle (position lX_section bY_stack 0) (position rX_r1 tY_stack 0) "SiO2" "R.gate2.gr1")
(sdegeo:create-rectangle (position rX_r1 bY_stack 0) (position rX_r2 tY_stack 0) "SiO2" "R.gate2.gr2")
(sdegeo:create-rectangle (position rX_r2 bY_stack 0) (position rX_r3 tY_stack 0) "SiO2" "R.gate2.gr3")

;;create regions under isolation 3
(define lX_section rX_g2)
(define Lgrid (/ Liso3 3))
(define rX_r1 (+ lX_section Lgrid)) ;region 1
(define rX_r2 (+ rX_r1 Lgrid)) ;region 2
(define rX_r3 (+ rX_r2 Lgrid)) ;region 3
(sdegeo:create-rectangle (position lX_section bY_stack 0) (position rX_r1 tY_stack 0) "SiO2" "R.iso3.gr1")
(sdegeo:create-rectangle (position rX_r1 bY_stack 0) (position rX_r2 tY_stack 0) "SiO2" "R.iso3.gr2")
(sdegeo:create-rectangle (position rX_r2 bY_stack 0) (position rX_r3 tY_stack 0) "SiO2" "R.iso3.gr3")

;;create regions under gate 3
(define lX_section rX_i3)
(define Lgrid (/ Lgate3 3))
(define rX_r1 (+ lX_section Lgrid)) ;region 1
(define rX_r2 (+ rX_r1 Lgrid)) ;region 2
(define rX_r3 (+ rX_r2 Lgrid)) ;region 3
(sdegeo:create-rectangle (position lX_section bY_stack 0) (position rX_r1 tY_stack 0) "SiO2" "R.gate3.gr1")
(sdegeo:create-rectangle (position rX_r1 bY_stack 0) (position rX_r2 tY_stack 0) "SiO2" "R.gate3.gr2")
(sdegeo:create-rectangle (position rX_r2 bY_stack 0) (position rX_r3 tY_stack 0) "SiO2" "R.gate3.gr3")

;;create regions under isolation 4
;(define lX_section rX_g3)
;(define Lgrid (/ Liso4 3))
;(define rX_r1 (+ lX_section Lgrid)) ;region 1
;(define rX_r2 (+ rX_r1 Lgrid)) ;region 2
;(define rX_r3 (+ rX_r2 Lgrid)) ;region 3
;(sdegeo:create-rectangle (position lX_section bY_stack 0) (position rX_r1 tY_stack 0) "SiO2" "R.iso4.gr1")
;(sdegeo:create-rectangle (position rX_r1 bY_stack 0) (position rX_r2 tY_stack 0) "SiO2" "R.iso4.gr2")
;(sdegeo:create-rectangle (position rX_r2 bY_stack 0) (position rX_r3 tY_stack 0) "SiO2" "R.iso4.gr3")
(sdegeo:create-rectangle (position rX_g3 bY_stack 0) (position rX_i4 tY_stack 0) "SiO2" "R.iso4.stack")

<end>

;create isolation and gate layer
(sdegeo:create-rectangle (position lX_stack tY_stack 0) (position rX_i1 tY_gate 0) "Nitride" "R.iso1")
(sdegeo:create-rectangle (position rX_i1 tY_stack 0) (position rX_g1 tY_gate 0) "TaN" "R.gate1")
(sdegeo:create-rectangle (position rX_g1 tY_stack 0) (position rX_i2 tY_gate 0) "Nitride" "R.iso2")
(sdegeo:create-rectangle (position rX_i2 tY_stack 0) (position rX_g2 tY_gate 0) "TaN" "R.gate2")
(sdegeo:create-rectangle (position rX_g2 tY_stack 0) (position rX_i3 tY_gate 0) "Nitride" "R.iso3")
(sdegeo:create-rectangle (position rX_i3 tY_stack 0) (position rX_g3 tY_gate 0) "TaN" "R.gate3")
(sdegeo:create-rectangle (position rX_g3 tY_stack 0) (position rX_i4 tY_gate 0) "Nitride" "R.iso4")

;contacts
(sdegeo:define-contact-set "gate1" (color:rgb 1.0 0.0 0.0) "##")
(sdegeo:define-contact-set "gate2" (color:rgb 0.0 1.0 0.0) "##")
(sdegeo:define-contact-set "gate3" (color:rgb 0.0 0.0 1.0) "##")
(sdegeo:define-contact-set "source" (color:rgb 1.0 1.0 0.0) "##")
(sdegeo:define-contact-set "drain" (color:rgb 0.0 1.0 1.0) "##")
(sdegeo:define-contact-set "substrate" (color:rgb 1.0 0.0 1.0) "##")

(sdegeo:define-2d-contact (find-edge-id (position (+ lX_i1 (/ Liso1 2)) tY_subs 0 )) "source")
(sdegeo:define-2d-contact (find-edge-id (position (+ rX_g3 (/ Liso4 2)) tY_subs 0 )) "drain")
(sdegeo:define-2d-contact (find-edge-id (position (/ (+ rX_i2 rX_g2) 2)  bY_subs 0 )) "substrate")

(sdegeo:set-current-contact-set "gate1")
(sdegeo:set-contact-boundary-edges (find-body-id (position (/ (+ rX_i1 rX_g1) 2) (/ (+ tY_stack tY_gate) 2) 0)))
(sdegeo:delete-region (find-body-id (position (/ (+ rX_i1 rX_g1) 2) (/ (+ tY_stack tY_gate) 2) 0)))
(sdegeo:set-current-contact-set "gate2")
(sdegeo:set-contact-boundary-edges (find-body-id (position (/ (+ rX_i2 rX_g2) 2) (/ (+ tY_stack tY_gate) 2) 0)))
(sdegeo:delete-region (find-body-id (position (/ (+ rX_i2 rX_g2) 2) (/ (+ tY_stack tY_gate) 2) 0)))
(sdegeo:set-current-contact-set "gate3")
(sdegeo:set-contact-boundary-edges (find-body-id (position (/ (+ rX_i3 rX_g3) 2) (/ (+ tY_stack tY_gate) 2) 0)))
(sdegeo:delete-region (find-body-id (position (/ (+ rX_i3 rX_g3) 2) (/ (+ tY_stack tY_gate) 2) 0)))



;doping
(sdedr:define-constant-profile "Const.Silicon" "BoronActiveConcentration" Nsubs)
(sdedr:define-constant-profile-region "PlaceCD" "Const.Silicon" "R.subs")

;junction
(sdedr:define-refeval-window "Baseline.iso1" "Line" (position lX_i1 bY_stack 0) (position (+ lX_i1 (* 1.0 Liso1)) bY_stack 0))
(sdedr:define-refeval-window "Baseline.iso2" "Line" (position (+ rX_g1 (* 0.0 Liso2)) bY_stack 0) (position (+ rX_g1 (* 1.0 Liso2)) bY_stack 0))
(sdedr:define-refeval-window "Baseline.iso3" "Line" (position (+ rX_g2 (* 0.0 Liso3)) bY_stack 0) (position (+ rX_g2 (* 1.0 Liso3)) bY_stack 0))
(sdedr:define-refeval-window "Baseline.iso4" "Line" (position (+ rX_g3 (* 0.0 Liso4)) bY_stack 0) (position rX_i4 bY_stack 0))

(define JErfLength (* 0.05 JDepth))
(sdedr:define-erf-profile "Erf.stack.iso" "PhosphorusActiveConcentration" "SymPos" JDepth "MaxVal" 1e20 "Length" JErfLength "Erf" "Factor" 0.2)
(sdedr:define-gaussian-profile "Gauss.stack.iso" "PhosphorusActiveConcentration" "PeakPos" 0.0 "PeakVal" 5e19 "ValueAtDepth" Nsubs "Depth" JDepth "Gauss" "Factor" 0.2)
(sdedr:define-analytical-profile-placement "PlaceAP.iso1" "Erf.stack.iso" "Baseline.iso1" "Negative" "NoReplace")
(sdedr:define-analytical-profile-placement "PlaceAP.iso2" "Erf.stack.iso" "Baseline.iso2" "Negative" "NoReplace")
(sdedr:define-analytical-profile-placement "PlaceAP.iso3" "Erf.stack.iso" "Baseline.iso3" "Negative" "NoReplace")
(sdedr:define-analytical-profile-placement "PlaceAP.iso4" "Erf.stack.iso" "Baseline.iso4" "Negative" "NoReplace")

;halo-like buried heavily-doped region under channel
(define HaloHalfLength (* 0.3 JDepth))
(define HaloCenterPos (- tY_subs (* 0.8 JDepth)))
(sdedr:define-gaussian-profile "Gauss.halo" "BoronActiveConcentration" "PeakPos" 0.0 "PeakVal" (* 10 Nsubs) "Length" HaloHalfLength "Gauss" "Factor" 0.05)
(sdedr:define-refeval-window "Baseline.halo.gate1" "Line" (position rX_i1 (- tY_subs (* 0.8 JDepth)) 0) (position rX_g1 HaloCenterPos 0))
(sdedr:define-refeval-window "Baseline.halo.gate2" "Line" (position rX_i2 (- tY_subs (* 0.8 JDepth)) 0) (position rX_g2 HaloCenterPos 0))
(sdedr:define-refeval-window "Baseline.halo.gate3" "Line" (position rX_i3 (- tY_subs (* 0.8 JDepth)) 0) (position rX_g3 HaloCenterPos 0))
(sdedr:define-analytical-profile-placement "PlaceAP.halo.gate1" "Gauss.halo" "Baseline.halo.gate1" "Both" "NoReplace")
(sdedr:define-analytical-profile-placement "PlaceAP.halo.gate2" "Gauss.halo" "Baseline.halo.gate2" "Both" "NoReplace")
(sdedr:define-analytical-profile-placement "PlaceAP.halo.gate3" "Gauss.halo" "Baseline.halo.gate3" "Both" "NoReplace")



;mesh strategy
;subs
(sdedr:define-refinement-size "Ref.subs" 20e-3  20e-3  10e-3  10e-3)
(sdedr:define-refinement-region "PlaceRef.subs" "Ref.subs" "R.subs")

;stack
(sdedr:define-refinement-size "Ref.stack" 5e-3  3e-3  1e-3  1e-3)
(sdedr:define-refinement-material "PlaceRef.stack" "Ref.stack" "SiO2")

;isolation region
(sdedr:define-refinement-size "Ref.iso" 20e-3  20e-3  15e-3  15e-3)
(sdedr:define-refinement-material "PlaceRef.iso" "Ref.iso" "Nitride")

;junction
(sdedr:define-refinement-size "Ref.junction" 8e-3  8e-3  1e-3  1e-3)
(sdedr:define-refinement-function "Ref.junction" "DopingConcentration" "MaxTransDiff" 0.5)
(sdedr:define-refeval-window "RefWin.junction.iso1" "Rectangle" (position lX_i1 tY_subs 0) (position (+ rX_i1 (* 0.2 Liso1)) (- tY_subs (+ (* 1.1 JErfLength) JDepth)) 0))
(sdedr:define-refeval-window "RefWin.junction.iso2" "Rectangle" (position (- rX_g1 (* 0.2 Liso2)) tY_subs 0) (position (+ rX_i2 (* 0.2 Liso2)) (- tY_subs (+ (* 1.2 JErfLength) JDepth)) 0))
(sdedr:define-refeval-window "RefWin.junction.iso3" "Rectangle" (position (- rX_g2 (* 0.2 Liso3)) tY_subs 0) (position (+ rX_i3 (* 0.2 Liso3)) (- tY_subs (+ (* 1.2 JErfLength) JDepth)) 0))
(sdedr:define-refeval-window "RefWin.junction.iso4" "Rectangle" (position (- rX_g3 (* 0.2 Liso4)) tY_subs 0) (position rX_i4 (- tY_subs (+ (* 1.1 JErfLength) JDepth) 0) 0))
(sdedr:define-refinement-placement "PlaceRF.junction.iso1" "Ref.junction" "RefWin.junction.iso1")
(sdedr:define-refinement-placement "PlaceRF.junction.iso2" "Ref.junction" "RefWin.junction.iso2")
(sdedr:define-refinement-placement "PlaceRF.junction.iso3" "Ref.junction" "RefWin.junction.iso3")
(sdedr:define-refinement-placement "PlaceRF.junction.iso4" "Ref.junction" "RefWin.junction.iso4")

;channel
(sdedr:define-refeval-window "RefWin.channel.gate1" "Rectangle" (position rX_i1 tY_subs 0) (position rX_g1 (- tY_subs ChDepth) 0))
(sdedr:define-refeval-window "RefWin.channel.gate2" "Rectangle" (position rX_i2 tY_subs 0) (position rX_g2 (- tY_subs ChDepth) 0))
(sdedr:define-refeval-window "RefWin.channel.gate3" "Rectangle" (position rX_i3 tY_subs 0) (position rX_g3 (- tY_subs ChDepth) 0))
(sdedr:define-multibox-size "MB.channel" 3e-3  3e-3  3e-3  0.1e-3  1  -1.1)
(sdedr:define-multibox-placement "PlaceMB.channel.gate1" "MB.channel" "RefWin.channel.gate1")
(sdedr:define-multibox-placement "PlaceMB.channel.gate2" "MB.channel" "RefWin.channel.gate2")
(sdedr:define-multibox-placement "PlaceMB.channel.gate3" "MB.channel" "RefWin.channel.gate3")

;halo
(sdedr:define-refinement-size "Ref.halo" 8e-3 8e-3 1e-3 1e-3)
(sdedr:define-refinement-function "Ref.halo" "DopingConcentration" "MaxTransDiff" 0.5)
(sdedr:define-refeval-window "RefWin.halo.gate1" "Rectangle" (position rX_i1 (- HaloCenterPos HaloHalfLength) 0) (position rX_g1 (+ HaloCenterPos HaloHalfLength) 0))
(sdedr:define-refeval-window "RefWin.halo.gate2" "Rectangle" (position rX_i2 (- HaloCenterPos HaloHalfLength) 0) (position rX_g2 (+ HaloCenterPos HaloHalfLength) 0))
(sdedr:define-refeval-window "RefWin.halo.gate3" "Rectangle" (position rX_i3 (- HaloCenterPos HaloHalfLength) 0) (position rX_g3 (+ HaloCenterPos HaloHalfLength) 0))
(sdedr:define-refinement-placement "PlaceRF.halo.gate1" "Ref.halo" "RefWin.halo.gate1")
(sdedr:define-refinement-placement "PlaceRF.halo.gate2" "Ref.halo" "RefWin.halo.gate2")
(sdedr:define-refinement-placement "PlaceRF.halo.gate3" "Ref.halo" "RefWin.halo.gate3")


(sde:build-mesh "snmesh" "" "triple")
