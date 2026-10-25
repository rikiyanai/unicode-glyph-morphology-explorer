#uselib "hspda.dll"
#func func_sortval sortval $0083
#func func_sortstr sortstr $0083
#func func_sortnote sortnote $0003
#func func_sortget sortget $0083
#func func_sortbye sortbye $0100
#func func_csvstr csvstr $0087
#func func_csvnote csvnote $0087
#func func_xnotesel xnotesel $0083
#func func_xnoteadd xnoteadd $0006
	var_0 = "アスキージャスティス Ver1.4"
	title var_0
	screen 0, 640, 544
	buffer 3, 800, 2400
	color 255, 255, 255
	boxf 0, 0, 800, 2400
	gsel 0
	color 96, 192, 128
	boxf 0, 0, 639, 63
	sdim var_1, 4096
	sdim var_2, 32, 5
	sdim var_3, 32000
	sdim var_4, 32000
	sdim var_5, 1024
	dim var_6, 8, 16
	dim var_7, 8, 16
	dim var_8, 8, 16, 3
	var_2 . 0 = "濃い"
	var_2 . 1 = "やや濃い"
	var_2 . 2 = "ふつう"
	var_2 . 3 = "やや薄い"
	var_2 . 4 = "薄い"
	sdim var_9, 32, 4
	var_9 . 0 = "h"
	var_9 . 1 = "f"
	var_9 . 2 = "k"
	var_9 . 3 = "s"
	var_10 = 15
	var_11 = 27
	var_12 = 3
	var_13 = var_10 + var_11 + var_12 / 3
	var_14 = 15
	var_15 = 27
	var_16 = 3
	var_17 = var_14 + var_15 + var_16 / 3
	var_18 = 0
	var_19 = 0
	dim var_20, 96, 8, 16
	dim var_21, 285
	dim var_22, 295
	var_23 = 2
	var_24 = 1
	var_25 = 4
	var_26 = 0
	var_27 = 0
	bload "mjdata14.dat", var_20
	bload "mjnodo14.dat", var_22
	sdim var_28, 512
	var_28 = " ,+!f%;^YgjMO()-=&$*0123456789:/?@Ae.'B\"C_DEF#JGhHILKNPQRSTUVWXZ[\\]c`abkdilmnopqrstuvwxyz{|}~"
	screen 5, 320, 480, 2, 0, 0
	color 192, 192, 192
	boxf 0, 0, 320, 480
	title "アスキージャスティス　ヘルプ"
	sdim var_29, 32000
	bload "hlpmes14.txt", var_29, 1252
	objsize 64, 24
	pos 128, 440
	button "閉じる", * label_1
	pos 0, 0
	mesbox var_29, 320, 420, 0
*label_2
	gsel 0
	clrobj
	color 140, 140, 140
	line 0, 0, 639, 0
	color 96, 96, 96
	line 0, 1, 639, 1
	color 220, 220, 220
	line 0, 60, 639, 60
	color 180, 180, 180
	line 0, 61, 639, 61
	color 140, 140, 140
	line 0, 62, 639, 62
	color 96, 96, 96
	line 0, 63, 639, 63
	objsize 96, 32
	pos 16, 6
	button "変換開始", * label_3
	pos 128, 6
	button "画像読込", * label_4
	color 0, 0, 0
	pos 256, 4
	mes "黒の濃さ"
	pos 256, 24
	combox var_23, 96, "濃い\nやや濃い\nふつう\nややうすい\nうすい"
	pos 360, 4
	mes "モード"
	pos 360, 24
	combox var_24, 96, "はやい\nふつう\nきれい\n最高級"
	pos 460, 4
	mes "グラデレベル"
	pos 460, 24
	combox var_25, 96, "8\n7\n6\n5\n4\n3\n2\n1\n輪郭1\n輪郭2\n輪郭3"
	objsize 64, 32
	pos 568, 20
	button "HELP", * label_5
	pos 16, 40
	objsize 16, 16
	chkbox "", var_18
	pos 32, 40
	mes "横640化"
	pos 128, 40
	objsize 16, 16
	chkbox "", var_19
	pos 144, 40
	mes "出力をhtml化"
	stop
*label_4
	dialog "jpg;*.bmp;", 16
	if stat = 0 {
		dialog "ファイルが選択されませんでした"
		stop
	}
	var_1 = refstr
	gsel 3
	picload var_1
	var_30 = winx
	var_31 = winy
	buffer 3, var_30, var_31 + 16
	color 255, 255, 255
	boxf var_30, var_31 + 16
	picload var_1, 1, 0, 0
	if var_18 = 1 {
		var_32 = ( var_31 * 6400 / var_30 / 160 ) * 16 + 16
		var_33 = 640
		if var_32 > 2400 {
			var_32 = 2400
		}
	}
	else {
		var_33 = ( var_30 / 8 ) * 8
		if var_33 > 640 {
			var_33 = 640
		}
		var_32 = ( var_31 / 16 ) * 16 + 16
		if var_32 > 2400 {
			var_32 = 2400
		}
	}
	var_26 = ( var_32 / 480 )
	var_34 = var_32 \ 480
	int var_35
	var_35 = ( var_33 / 8 ) * ( var_32 / 16 )
	str var_35
	gsel 0
	color 255, 255, 255
	boxf 0, 64, 639, 543
	pos 0, 64
	if var_18 = 1 {
		gzoom 640, 480, 3, 0, 0, var_30, ( var_30 * 4800 / 64 ) / 100
	}
	else {
		gcopy 3, 0, 0, 640, 480
	}
	var_27 = 1
	stop
*label_3
	var_36 = var_25
	if var_27 = 0 {
		dialog "画像を読み込んでください"
		goto * label_6
	}
	if var_18 = 1 {
		var_32 = ( var_31 * 6400 / var_30 / 160 ) * 16 + 16
		var_33 = 640
		if var_32 > 2400 {
			var_32 = 2400
		}
	}
	else {
		var_33 = ( var_30 / 8 ) * 8
		if var_33 > 640 {
			var_33 = 640
		}
		var_32 = ( var_31 / 16 ) * 16 + 16
		if var_32 > 2400 {
			var_32 = 2400
		}
	}
	var_26 = ( var_32 / 480 )
	var_34 = var_32 \ 480
	int var_35
	var_35 = ( var_33 / 8 ) * ( var_32 / 16 )
	str var_35
	gsel 0
	var_37 = ( 235 * 3 ) - ( var_23 * 80 )
	if var_23 = 0 {
		var_37 = var_37 - 15
	}
	clrobj
	color 96, 192, 128
	boxf 0, 0, 639, 63
	color 140, 140, 140
	line 0, 0, 639, 0
	color 96, 96, 96
	line 0, 1, 639, 1
	color 220, 220, 220
	line 0, 60, 639, 60
	color 180, 180, 180
	line 0, 61, 639, 61
	color 140, 140, 140
	line 0, 62, 639, 62
	color 96, 96, 96
	line 0, 63, 639, 63
	pos 16, 16
	objsize 96, 32
	button "変換停止", * label_6
	sdim var_3, 32000
	repeat ( var_26 + 1 )
		var_38 = cnt
		color 255, 255, 255
		boxf 0, 64, 640, 480 + 64
		pos 0, 64
		color 255, 255, 255
		if var_18 = 1 {
			gzoom 640, 480, 3, 0, ( var_38 * ( ( var_30 * 4800 / 64 ) / 100 ) ), var_30, ( var_30 * 4800 / 64 ) / 100
		}
		else {
			gcopy 3, 0, ( var_38 * 480 ), 640, 480
		}
		color 0, 0, 0
		if var_38 ! var_26 {
			var_39 = 480 / 16
		}
		else {
			var_39 = var_34 / 16
		}
		repeat var_39
			var_40 = cnt
			repeat ( var_33 / 8 )
				await 0
				var_41 = cnt
				int var_42
				var_43 = var_40 * ( var_33 / 8 ) + var_41 + ( var_38 * ( var_33 / 8 ) * 30 )
				str var_43
				title var_43 + "/" + var_35 + "文字"
				dim var_21, 285
				var_44 = 0
				var_45 = 0
				var_46 = 0
				if var_25 < 8 {
					if var_24 = 0 {
						var_47 = 15
						gosub * label_10
					}
					if var_24 = 1 {
						var_47 = 48
						gosub * label_11
					}
					if var_24 = 2 {
						var_47 = 93
						gosub * label_12
					}
					if var_24 = 3 {
						var_47 = 279
						gosub * label_13
					}
				}
				if var_25 >= 8 {
					gosub * label_14
					if var_48 = 0 {
						var_46 = 1
						color 255, 255, 255
						boxf var_41 * 8, ( var_40 * 16 ) + 64, ( var_41 * 8 ) + 7, ( var_40 * 16 ) + 15 + 64
						goto * label_15
					}
					if var_24 = 0 {
						var_47 = 15
						gosub * label_16
					}
					if var_24 = 1 {
						var_47 = 48
						gosub * label_17
					}
					if var_24 = 2 {
						var_47 = 279
						gosub * label_18
					}
					if var_24 = 3 {
						var_47 = 279
						gosub * label_19
					}
				}
*label_15
				if var_46 = 1 {
					var_49 = " "
					goto * label_20
				}
				if var_46 = 2 {
					var_49 = "M"
					goto * label_20
				}
				var_44 = var_44 / 255
				var_44 = var_44 * ( var_44 / 10 + 70 ) / 70
				if var_44 > 255 {
					var_44 = 255
				}
				func_sortval var_21, 1
				var_50 = 0
				var_51 = 99999
				var_52 = 0
				repeat var_47
					func_sortget var_53, cnt
					var_53 = var_53 \ 93
					var_49 = ( var_22 . var_53 * 11 / 3 ) - var_44
					var_49 = var_49 * var_49
					if var_49 < ( ( var_36 + 2 ) * ( var_36 + 2 ) * 60 ) {
						var_50 = 1
						break
					}
					if ( var_49 < var_51 ) & ( cnt < 5 ) {
						var_51 = var_49
						var_52 = cnt
					}
				loop
				if var_50 = 0 {
					func_sortget var_53, 0
				}
				if var_53 > 92 {
					var_53 = var_53 \ 93
				}
				strmid var_49, var_28, var_53, 1
				if var_49 = "M" {
					if var_50 = 0 {
						func_sortget var_53, var_52
						if var_53 > 92 {
							var_53 = var_53 \ 93
						}
						strmid var_49, var_28, var_53, 1
					}
				}
*label_20
				color 0, 0, 0
				pos var_41 * 8, ( var_40 * 16 + 64 )
				mes var_49
				var_3 = var_3 + var_49
			loop
			var_3 = var_3 + "\n"
		loop
	loop
	var_36 = 8 - var_36
	str var_36
	if var_25 >= 8 {
		int var_54
		var_54 = var_25 - 7
		str var_54
		var_36 = "輪郭" + var_54
	}
	if var_19 = 0 {
		int var_55
		strlen var_55, var_3
		bsave var_1 + var_2 . var_23 + var_9 . var_24 + "gr" + var_36 + ".txt", var_3, var_55
	}
	else {
		var_3 = "<HTML>\n<HEAD>\n<TITLE>\n</TITLE>\n</HEAD>\n<BODY>\n<pre>\n" + var_3
		var_5 = "</pre>\n</BODY>\n</HTML>\n\n"
		var_4 = var_3 + var_5
		strlen var_55, var_4
		bsave var_1 + var_2 . var_23 + var_9 . var_24 + "gr" + var_36 + ".html", var_4, var_55
	}
	int var_25
	int var_36
	var_36 = 8 - var_36
	dialog "終了しました"
	title var_0
	color 255, 255, 255
	boxf 0, 64, 639, 543
	pos 0, 64
	if var_18 = 1 {
		gzoom 640, 480, 3, 0, 0, var_30, ( var_30 * 4800 / 64 ) / 100
	}
	else {
		gcopy 3, 0, 0, 640, 480
	}
	goto * label_2
*label_6
	dialog "変換を停止します。"
	title var_0
	pos 0, 64
	if var_18 = 1 {
		gzoom 640, 480, 3, 0, 0, var_30, ( var_30 * 4800 / 64 ) / 100
	}
	else {
		gcopy 3, 0, 0, 640, 480
	}
	goto * label_2
*label_13
	dim var_56, 8, 16
	var_57 = 0
	repeat 8
		var_58 = cnt
		repeat 16
			var_59 = 0
			var_60 = cnt
			pget ( var_41 * 8 ) + var_58, ( var_40 * 16 ) + var_60 + 64
			var_61 = rval + gval + bval
			var_59 = 255 - ( ( ( rval * var_14 ) + ( gval * var_15 ) + ( bval * var_16 ) ) / var_17 / 3 )
			var_59 = var_59 - 40
			if var_59 < 0 var_62 var_59 = 0 {
			}
			var_59 = var_59 * 256 / ( 256 - 40 )
			var_44 = var_44 + var_59
			var_63 = ( ( rval * var_14 ) + ( gval * var_15 ) + ( bval * var_16 ) ) / var_17 / var_37
			if var_63 ! 0 {
				var_63 = 1
			}
			var_56 . var_58 . var_60 = var_63
			if var_61 > 730 {
				var_57 = var_57 + 1
			}
			if var_61 < 32 {
				var_57 = var_57 - 1
			}
		loop
	loop
	if var_57 > 120 {
		var_46 = 1
		return
	}
	if var_57 < -120 {
		var_46 = 2
		return
	}
	repeat 3
		var_64 = cnt
		repeat 7
			var_58 = cnt
			if var_58 = 7 {
				dialog "777"
			}
			repeat 8
				var_60 = cnt * 2 + ( var_58 / 2 \ 2 )
				if var_64 = 0 {
					var_65 = var_58
					var_57 = var_56 . var_58 . var_60
				}
				if var_64 = 1 {
					if var_58 = 7 {
						dialog "7"
					}
					var_49 = var_58 + 1
					var_65 = var_58
					var_57 = var_56 . var_49 . var_60
				}
				if var_64 = 2 {
					if var_58 = 7 {
						dialog "77"
					}
					var_49 = var_58
					var_65 = var_58 + 1
					var_57 = var_56 . var_49 . var_60
				}
				if var_57 = 0 {
					repeat 48
						var_66 = cnt + ( var_64 * 93 )
						var_67 = var_66 \ 93
						var_21 . var_66 = var_21 . var_66 + ( ( 6 - ( var_20 . var_67 . var_65 . var_60 * 5 ) ) * 3 )
					loop
				}
				else {
					repeat 48
						var_66 = cnt + ( var_64 * 93 )
						var_67 = var_66 \ 93
						var_21 . var_66 = var_21 . var_66 + ( ( -6 + ( var_20 . var_67 . var_65 . var_60 * 8 ) ) * 3 )
					loop
				}
			loop
		loop
	loop
	return
*label_12
	var_57 = 0
	repeat 8
		var_58 = cnt
		repeat 8
			var_59 = 0
			var_60 = cnt * 2 + ( var_58 / 2 \ 2 )
			pget ( var_41 * 8 ) + var_58, ( var_40 * 16 ) + var_60 + 64
			var_59 = rval + gval + bval
			if var_59 > 730 {
				var_57 = var_57 + 1
			}
			if var_59 < 32 {
				var_57 = var_57 - 1
			}
		loop
	loop
	if var_57 > 60 {
		var_46 = 1
		return
	}
	if var_57 < -60 {
		var_46 = 2
		return
	}
	repeat 8
		var_58 = cnt
		repeat 8
			var_60 = cnt * 2 + ( var_58 / 2 \ 2 )
			var_57 = 0
			pget ( var_41 * 8 ) + var_58, ( var_40 * 16 ) + var_60 + 64
			var_57 = ( ( rval * var_14 ) + ( gval * var_15 ) + ( bval * var_16 ) ) / var_17 / var_37
			var_59 = 255 - ( ( ( rval * var_14 ) + ( gval * var_15 ) + ( bval * var_16 ) ) / var_17 / 3 )
			var_59 = var_59 - 40
			if var_59 < 0 var_62 var_59 = 0 {
			}
			var_59 = var_59 * 256 / ( 256 - 40 )
			if var_57 ! 0 {
				var_57 = 1
			}
			var_44 = var_44 + ( var_59 * 2 )
			if var_57 = 0 {
				repeat 93
					var_66 = cnt
					var_21 . var_66 = var_21 . var_66 + ( ( 6 - ( var_20 . var_66 . var_58 . var_60 * 5 ) ) * 3 )
				loop
			}
			else {
				repeat 93
					var_66 = cnt
					var_21 . var_66 = var_21 . var_66 + ( ( -6 + ( var_20 . var_66 . var_58 . var_60 * 8 ) ) * 3 )
				loop
			}
		loop
	loop
	return
*label_10
	var_57 = 0
	repeat 4
		var_58 = cnt
		repeat 8
			var_60 = cnt
			var_59 = 0
			var_65 = var_58 * 2 + ( var_58 \ 2 )
			var_68 = var_60 * 2
			pget ( var_41 * 8 ) + var_65, ( var_40 * 16 ) + var_68 + 64
			var_59 = rval + gval + bval
			if var_59 > 730 {
				var_57 = var_57 + 1
			}
			if var_59 < 32 {
				var_57 = var_57 - 1
			}
		loop
	loop
	if var_57 > 30 {
		var_46 = 1
		return
	}
	if var_57 < -30 {
		var_46 = 2
		return
	}
	repeat 4
		var_58 = cnt
		repeat 8
			var_60 = cnt
			var_57 = 0
			var_65 = var_58 * 2 + ( var_58 \ 2 )
			var_68 = var_60 * 2
			pget ( var_41 * 8 ) + var_65, ( var_40 * 16 ) + var_68 + 64
			var_57 = ( ( rval * var_10 ) + ( gval * var_11 ) + ( bval * var_12 ) ) / var_13 / var_37
			if var_57 ! 0 {
				var_57 = 1
			}
			var_59 = 255 - ( ( ( rval * var_10 ) + ( gval * var_11 ) + ( bval * var_12 ) ) / var_13 / 3 )
			var_44 = var_44 + ( var_59 * 4 )
			if var_57 = 0 {
				repeat 15
					var_66 = cnt
					var_21 . var_66 = var_21 . var_66 + ( ( 6 - ( var_20 . var_66 . var_65 . var_68 * 5 ) ) * 3 )
				loop
			}
			else {
				repeat 15
					var_66 = cnt
					var_21 . var_66 = var_21 . var_66 + ( ( -6 + ( var_20 . var_66 . var_65 . var_68 * 8 ) ) * 3 )
				loop
			}
		loop
	loop
	return
*label_11
	var_57 = 0
	repeat 8
		var_58 = cnt
		repeat 8
			var_59 = 0
			var_60 = cnt * 2 + ( var_58 / 2 \ 2 )
			pget ( var_41 * 8 ) + var_58, ( var_40 * 16 ) + var_60 + 64
			var_59 = rval + gval + bval
			if var_59 > 730 {
				var_57 = var_57 + 1
			}
			if var_59 < 32 {
				var_57 = var_57 - 1
			}
		loop
	loop
	if var_57 > 60 {
		var_46 = 1
		return
	}
	if var_57 < -60 {
		var_46 = 2
		return
	}
	repeat 8
		var_58 = cnt
		repeat 8
			var_60 = cnt
			var_57 = 0
			var_65 = var_58
			var_68 = var_60 * 2 + ( var_58 / 2 \ 2 )
			var_57 = 0
			pget ( var_41 * 8 ) + var_65, ( var_40 * 16 ) + var_68 + 64
			var_57 = ( ( rval * var_10 ) + ( gval * var_11 ) + ( bval * var_12 ) ) / var_13 / var_37
			var_59 = 255 - ( ( ( rval * var_10 ) + ( gval * var_11 ) + ( bval * var_12 ) ) / var_13 / 3 )
			pget ( var_41 * 8 ) + var_65, ( var_40 * 16 ) + var_68 + 65
			var_57 = ( var_57 + ( ( ( rval * var_10 ) + ( gval * var_11 ) + ( bval * var_12 ) ) / var_13 / var_37 ) ) / 2
			var_59 = ( var_59 + 255 - ( ( ( rval * var_10 ) + ( gval * var_11 ) + ( bval * var_12 ) ) / var_13 / 3 ) ) / 2
			if var_57 ! 0 {
				var_57 = 1
			}
			var_44 = var_44 + ( var_59 * 2 )
			if var_57 = 0 {
				repeat 48
					var_66 = cnt
					var_21 . var_66 = var_21 . var_66 + ( ( 6 - ( var_20 . var_66 . var_65 . var_68 * 5 ) ) * 3 )
				loop
			}
			else {
				repeat 48
					var_66 = cnt
					var_21 . var_66 = var_21 . var_66 + ( ( -6 + ( var_20 . var_66 . var_65 . var_68 * 8 ) ) * 3 )
				loop
			}
		loop
	loop
	return
*label_19
	color 255, 255, 255
	boxf var_41 * 8, ( var_40 * 16 ) + 64, ( var_41 * 8 ) + 7, ( var_40 * 16 ) + 15 + 64
	repeat 8
		var_58 = cnt
		repeat 16
			var_60 = cnt
			var_57 = 1 - var_6 . var_58 . var_60
			var_44 = var_44 + ( var_6 . var_58 . var_60 * 4 )
			if var_57 = 0 {
				color 255, 0, 0
				pset ( var_41 * 8 ) + var_58, ( var_40 * 16 ) + var_60 + 64
			}
		loop
	loop
	repeat 3
		var_64 = cnt
		repeat 7
			var_58 = cnt
			if var_58 = 7 {
				dialog "777"
			}
			repeat 8
				var_60 = cnt * 2 + ( var_58 / 2 \ 2 )
				if var_64 = 0 {
					var_65 = var_58
					var_57 = var_6 . var_58 . var_60
				}
				if var_64 = 1 {
					if var_58 = 7 {
						dialog "7"
					}
					var_49 = var_58 + 1
					var_65 = var_58
					var_57 = var_6 . var_49 . var_60
				}
				if var_64 = 2 {
					if var_58 = 7 {
						dialog "77"
					}
					var_49 = var_58
					var_65 = var_58 + 1
					var_57 = var_6 . var_49 . var_60
				}
				var_57 = 1 - var_57
				if var_57 = 0 {
					repeat 93
						var_66 = cnt + ( var_64 * 93 )
						var_67 = var_66 \ 93
						var_21 . var_66 = var_21 . var_66 + ( ( 6 - ( var_20 . var_67 . var_65 . var_60 * 5 ) ) * 3 )
					loop
				}
				else {
					repeat 93
						var_66 = cnt + ( var_64 * 93 )
						var_67 = var_66 \ 93
						var_21 . var_66 = var_21 . var_66 + ( ( -6 + ( var_20 . var_67 . var_65 . var_60 * 8 ) ) * 3 )
					loop
				}
			loop
		loop
	loop
	return
*label_18
	color 255, 255, 255
	boxf var_41 * 8, ( var_40 * 16 ) + 64, ( var_41 * 8 ) + 7, ( var_40 * 16 ) + 15 + 64
	repeat 8
		var_58 = cnt
		repeat 16
			var_60 = cnt
			var_57 = 1 - var_6 . var_58 . var_60
			var_44 = var_44 + ( var_6 . var_58 . var_60 * 4 )
			if var_57 = 0 {
				color 255, 0, 0
				pset ( var_41 * 8 ) + var_58, ( var_40 * 16 ) + var_60 + 64
			}
		loop
	loop
	repeat 3
		var_64 = cnt
		repeat 7
			var_58 = cnt
			if var_58 = 7 {
				dialog "777"
			}
			repeat 8
				var_60 = cnt * 2 + ( var_58 / 2 \ 2 )
				if var_64 = 0 {
					var_65 = var_58
					var_57 = var_6 . var_58 . var_60
				}
				if var_64 = 1 {
					if var_58 = 7 {
						dialog "7"
					}
					var_49 = var_58 + 1
					var_65 = var_58
					var_57 = var_6 . var_49 . var_60
				}
				if var_64 = 2 {
					if var_58 = 7 {
						dialog "77"
					}
					var_49 = var_58
					var_65 = var_58 + 1
					var_57 = var_6 . var_49 . var_60
				}
				var_57 = 1 - var_57
				if var_57 = 0 {
					repeat 48
						var_66 = cnt + ( var_64 * 93 )
						var_67 = var_66 \ 93
						var_21 . var_66 = var_21 . var_66 + ( ( 6 - ( var_20 . var_67 . var_65 . var_60 * 5 ) ) * 3 )
					loop
				}
				else {
					repeat 48
						var_66 = cnt + ( var_64 * 93 )
						var_67 = var_66 \ 93
						var_21 . var_66 = var_21 . var_66 + ( ( -6 + ( var_20 . var_67 . var_65 . var_60 * 8 ) ) * 3 )
					loop
				}
			loop
		loop
	loop
	return
*label_16
	color 255, 255, 255
	boxf var_41 * 8, ( var_40 * 16 ) + 64, ( var_41 * 8 ) + 7, ( var_40 * 16 ) + 15 + 64
	repeat 8
		var_58 = cnt
		repeat 8
			var_60 = cnt
			var_65 = var_58
			var_68 = var_60 * 2 + ( var_58 / 2 \ 2 )
			var_57 = 1 - var_6 . var_65 . var_68
			var_44 = var_44 + ( var_6 . var_58 . var_60 * 12 )
			if var_57 = 0 {
				color 255, 0, 0
				pset ( var_41 * 8 ) + var_65, ( var_40 * 16 ) + var_68 + 64
			}
			if var_57 = 0 {
				repeat 15
					var_66 = cnt
					var_21 . var_66 = var_21 . var_66 + ( ( 6 - ( var_20 . var_66 . var_65 . var_68 * 5 ) ) * 3 )
				loop
			}
			else {
				repeat 15
					var_66 = cnt
					var_21 . var_66 = var_21 . var_66 + ( ( -6 + ( var_20 . var_66 . var_65 . var_68 * 8 ) ) * 3 )
				loop
			}
		loop
	loop
	return
*label_17
	color 255, 255, 255
	boxf var_41 * 8, ( var_40 * 16 ) + 64, ( var_41 * 8 ) + 7, ( var_40 * 16 ) + 15 + 64
	repeat 8
		var_58 = cnt
		repeat 8
			var_60 = cnt
			var_65 = var_58
			var_68 = var_60 * 2 + ( var_58 / 2 \ 2 )
			var_57 = 1 - var_6 . var_65 . var_68
			var_44 = var_44 + ( var_6 . var_58 . var_60 * 12 )
			if var_57 = 0 {
				color 255, 0, 0
				pset ( var_41 * 8 ) + var_65, ( var_40 * 16 ) + var_68 + 64
			}
			if var_57 = 0 {
				repeat 48
					var_66 = cnt
					var_21 . var_66 = var_21 . var_66 + ( ( 6 - ( var_20 . var_66 . var_65 . var_68 * 5 ) ) * 3 )
				loop
			}
			else {
				repeat 48
					var_66 = cnt
					var_21 . var_66 = var_21 . var_66 + ( ( -6 + ( var_20 . var_66 . var_65 . var_68 * 8 ) ) * 3 )
				loop
			}
		loop
	loop
	return
*label_14
	var_48 = 0
	var_69 = var_23 * 12 + 16
	var_69 = var_69 * var_69
	dim var_6, 8, 16
	dim var_7, 8, 16
	dim var_8, 8, 16, 3
	repeat 8
		var_58 = cnt
		repeat 16
			var_60 = cnt
			pget ( var_41 * 8 ) + var_58, ( var_40 * 16 ) + var_60 + 64
			var_8 . var_58 . var_60 . 0 = rval
			var_8 . var_58 . var_60 . 1 = gval
			var_8 . var_58 . var_60 . 2 = bval
		loop
	loop
	repeat 8
		var_58 = cnt
		repeat 14
			var_60 = cnt
			var_68 = var_60 + 1
			var_70 = var_68 + 1
			var_71 = var_8 . var_58 . var_60 . 0 - var_8 . var_58 . var_68 . 0
			var_72 = var_8 . var_58 . var_60 . 1 - var_8 . var_58 . var_68 . 1
			var_73 = var_8 . var_58 . var_60 . 2 - var_8 . var_58 . var_68 . 2
			var_71 = var_71 * var_71
			var_72 = var_72 * var_72
			var_73 = var_73 * var_73
			if ( var_71 > var_69 ) | ( var_72 > var_69 ) | ( var_73 > var_69 ) {
				var_48 = 1
				gosub * label_73
			}
		loop
	loop
	repeat 6
		var_58 = cnt
		var_65 = var_58 + 1
		var_74 = var_65 + 1
		repeat 16
			var_60 = cnt
			var_71 = var_8 . var_58 . var_60 . 0 - var_8 . var_65 . var_60 . 0
			var_72 = var_8 . var_58 . var_60 . 1 - var_8 . var_65 . var_60 . 1
			var_73 = var_8 . var_58 . var_60 . 2 - var_8 . var_65 . var_60 . 2
			var_71 = var_71 * var_71
			var_72 = var_72 * var_72
			var_73 = var_73 * var_73
			if ( var_71 > var_69 ) | ( var_72 > var_69 ) | ( var_73 > var_69 ) {
				var_48 = 1
				gosub * label_76
			}
		loop
	loop
	return
*label_73
	var_6 . var_58 . var_60 = 1
	if var_25 = 8 {
		return
	}
	var_6 . var_58 . var_68 = 1
	if var_25 = 9 {
		return
	}
	var_6 . var_58 . var_70 = 1
	return
*label_76
	var_6 . var_58 . var_60 = 1
	if var_25 = 8 {
		return
	}
	var_6 . var_65 . var_60 = 1
	if var_25 = 9 {
		return
	}
	var_6 . var_74 . var_60 = 1
	return
*label_5
	gsel 5, 1
	stop
*label_1
	gsel 5, - 1
	stop
	end
