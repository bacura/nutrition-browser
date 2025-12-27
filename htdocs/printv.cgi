#! /usr/bin/ruby
#encoding: utf-8
#Nutrition browser 2020 print web page 0.2.12 (2025/12/27)

#==============================================================================
# STATIC
#==============================================================================
@debug = false
fct_num = 14
frct_select = %w( 四捨五入 四捨五入 切り上げ 切り捨て )
accu_check = %w( 通常合計 精密合計 )
ew_check = %w( 単純g 予想g )
x_account = '@ho_meow'

#==============================================================================
# LIBRARY
#==============================================================================
require './soul'
require './brain'
require 'rqrcode'

#==============================================================================
# DEFINITION
#==============================================================================

# Language pack
def language_pack( language )
	l = Hash.new

	#Japanese
	l['ja'] = {
		viewer: 		"ビューアー"
	}

	return l[language]
end

#### html_header for printv
def html_head_pv( recipe, x_account )
	code = recipe.code
	media_code = recipe.media
	recipe_name = recipe.name
	x_image = ''
	x_image = "<meta name='twitter:image' content='#{$MYURL}#{$PHOTO}/#{media_code[0]}-tn.jpg' />" if media_code.size > 0

	html = <<-"HTML"
<!DOCTYPE html>
<head>
 	<title>栄養ブラウザ レシピ：#{recipe_name}</title>
 	<meta charset="UTF-8">
 	<meta name="keywords" content="栄養,nutrition, Nutritionist, food,検索,計算,解析,評価">
 	<meta name="description" content="食品成分表の検索,栄養計算,栄養評価, analysis, calculation">
 	<meta name="robots" content="index,follow">
 	<meta name="author" content="Shinji Yoshiyama">

 	<!-- Twitter card -->
 	<meta name="twitter:card" content="summary" />
 	<meta name="twitter:site" content="#{x_account}" />
 	<meta name="twitter:title" content="ユビキタス栄養ツール：栄養ブラウザ" />
 	<meta name="twitter:description" content="公開レシピ紹介///#{recipe_name}" />
 	#{x_image}
 	<meta name="twitter:image:alt" content="ばきゅら京都Labロゴ" />

  <!-- Jquery -->
  #{$JQUERY}
  <!-- <script type="text/javascript" src="./jquery-3.6.0.min.js"></script> -->

  <!-- bootstrap -->
  #{$BS_CSS}
  #{$BS_JS}
  <!-- <link rel="stylesheet" href="bootstrap-dist/css/bootstrap.min.css"> -->
  <!-- <script type="text/javascript" src="bootstrap-dist/js/bootstrap.min.js"></script> -->

 	<link rel="stylesheet" href="#{$CSS_PATH}/core.css">
	<script type="text/javascript" src="#{$JS_PATH}/core.js"></script>

	#{tracking()}
</head>

<body class="body">
  <span class="world_frame" id="world_frame">
HTML

  puts html
end


#### QRコード生成
def makeQRcode( text, code )
	qrcode = RQRCode::QRCode.new( text, :level => :m )

	# With default options specified explicitly
	png = qrcode.as_png(
		resize_gte_to: false,
		resize_exactly_to: false,
		fill: 'white',
		color: 'black',
		size: 100,
		border_modules: 4,
		module_px_size: 6,
		file: nil # path to write
	)
	IO.write( "#{$PHOTO_PATH}/#{code}-qr.png", png.to_s )
end


#### 食材抽出
def extract_foods( db, recipe, dish, template, ew_mode )
	sum = recipe.sum
	dish_recipe = recipe.dish
	uname = recipe.user.name
	calc_weight = [ '単純換算g','予想摂取g' ]
	return_foods = "<table class='table table-sm'>\n"

	case template
	when 0
		return_foods << "<thead><tr><th class='align_l'>食材</th><th class='align_r'>数量</th><th class='align_r'>単位</th></tr></thead>\n"
	when 1
		return_foods << "<thead><tr><th class='align_l'>食材</th><th class='align_l'>備考</th><th class='align_r'>数量</th><th class='align_r'>単位</th></tr></thead>\n"
	when 2
		return_foods << "<thead><tr><th>食品番号</th><th class='align_l'>食材</th><th class='align_l'>備考</th><th class='align_r'>数量</th><th class='align_r'>単位</th><th class='align_r'>#{calc_weight[ew_mode]}</th></tr></thead>\n"
	when 3
		return_foods << "<thead><tr><th>食品番号</th><th class='align_l'>食材</th><th class='align_l'>備考</th><th class='align_r'>数量</th><th class='align_r'>単位</th><th class='align_r'>#{calc_weight[ew_mode]}</th><th class='align_r'>廃棄率%</th><th class='align_r'>発注量kg</th></tr></thead>\n"
	end

	a = sum.split( "\t" )
	a.each do |e|
		fn, fw, fu, fuv, fc, fi, frr, few = e.split( ':' )
		few = fw if few == nil

		if fn == '-'
			return_foods << "<tr style='line-height:0.1em; background-color:whitesmoke;'><td></td><td>&nbsp;</td><td></td></tr>\n"
		elsif fn == '+'
			return_foods << "<tr style='line-height:0.5em; background-color:lemonchiffon;'><td></td><td>(#{fi})</td><td></td></tr>\n"
		else
			# 人数分調整
			z, fuv = food_weight_check( fuv ) if /\// =~ fuv
			fuv = BigDecimal( fuv ) / dish_recipe * dish
			fuv_v = unit_value( fuv )
			few = BigDecimal( few ) / dish_recipe * dish
			few_v = unit_value( few )

			res = db.query( "SELECT * from #{$TB_TAG} WHERE FN=?", false, [fn] )&.first

			case template
			when 0
  				class_add = ''
  				if /\+/ =~ res['class1']
    				class_add = "<span class='tagc'>#{res['class1'].sub( '+', '' )}</span> "
  				elsif /\+/ =~ res['class2']
    				class_add = "<span class='tagc'>#{res['class2'].sub( '+', '' )}</span> "
  				elsif /\+/ =~ res['class3']
    				class_add = "<span class='tagc'>#{res['class3'].sub( '+', '' )}</span> "
  				end
  				food_name = res['name']
				if /^\=/ =~ fi
					food_name = fi.sub( '=', '' )
					fi = ''
				end
				return_foods << "<tr><td>#{class_add}#{food_name}</td><td align='right'>#{fuv_v.ceil( 1 )}</td><td align='right'>#{fu}</td></tr>\n" if res

			when 1
				tags = tagnames( res )
				if /^\=/ =~ fi
					tags = fi.sub( '=', '' )
					fi = ''
				end
				return_foods << "<tr><td>#{tags}</td><td>#{fi}</td><td align='right'>#{fuv_v.ceil( 1 )}</td><td align='right'>#{fu}</td></tr>\n" if res

			when 2
				tags = tagnames( res )
				if /^\=/ =~ fi
					fi = fi.sub!( '=', '' )
				end
				return_foods << "<tr><td>#{fn}</td><td>#{tags}</td><td>#{fi}</td><td align='right'>#{fuv_v.ceil( 1 )}</td><td align='right'>#{fu}</td><td align='right'>#{few_v.ceil( 1 )}</td></tr>\n" if res

			when 3
				tags = tagnames( res )
				fi.sub!( '=', '' )
				refuse = 0
				query = ''
				if /^U/ =~ fn
					res = db.query( "SELECT * from #{$TB_FCTP} WHERE FN=? AND user=?", false, [fn, uname] )&.first
				elsif /^P/ =~ fn
					res = db.query( "SELECT * from #{$TB_FCTP} WHERE FN=?", false, [fn] )&.first
				else
					res = db.query( "SELECT REFUSE from #{$TB_FCT} WHERE FN=?", false, [fn] )&.first
				end
				refuse = res['REFUSE'].to_i if res
				if fuv >= 10
					t = ( fuv / ( 100 - refuse ) / BigDecimal( 10 )).ceil( 2 ).to_f.to_s
				else
					t = ( fuv / ( 100 - refuse ) / BigDecimal( 10 )).ceil( 3 ).to_f.to_s
				end
				df = t.split( '.' )
				comp = ( 2 - df[1].size )
				comp.times do |c| df[1] = df[1] << '0' end
				ordering_weight = df[0] + '.' + df[1]
				return_foods << "<tr><td>#{fn}</td><td>#{tags}</td><td>#{fi}</td><td align='right'>#{fuv_v.ceil( 1 )}</td><td align='right'>#{fu}</td><td align='right'>#{few_v.ceil( 1 )}</td><td align='right'>#{res['REFUSE']}</td><td align='right'>#{ordering_weight}</td></tr>\n" if res
			end
		end
	end

	return_foods << "</table>\n"

	return return_foods
end


#### 食材抽出・参照
def extract_ref_foods( db, recipe )
	sum = recipe.sum
	dish_recipe = recipe.dish
	uname = recipe.user.name
	calc_weight = [ '単純換算g','予想摂取g' ]
	return_foods = "<table class='table table-sm' style='font-size:x-small'>"
	return_foods << "<thead><tr><th class='align_l'>食材</th><th class='align_r'>数量</th><th class='align_r'>単位</th></tr></thead>"

	a = sum.split( "\t" )
	a.each do |e|
		fn, fw, fu, fuv, fc, fi, frr, few = e.split( ':' )
		few = fw if few == nil

		if fn == '-'
			return_foods << "<tr><td></td></tr>\n"
		elsif fn == '+'
			return_foods << "<tr><td class='print_subtitle'>#{fi}</td></tr>\n"
		else
			# 人数分調整
			z, fuv = food_weight_check( fuv ) if /\// =~ fuv
			fuv = BigDecimal( fuv )
			fuv_v = unit_value( fuv )
			few = BigDecimal( few )
			few_v = unit_value( few )

			res = db.query( "SELECT * from #{$TB_TAG} WHERE FN=?", false, [fn] )&.first

			class_add = ''
			if /\+/ =~ res['class1']
				class_add = "<span class='tagc'>#{res['class1'].sub( '+', '' )}</span> "
			elsif /\+/ =~ res['class2']
				class_add = "<span class='tagc'>#{res['class2'].sub( '+', '' )}</span> "
			elsif /\+/ =~ res['class3']
				class_add = "<span class='tagc'>#{res['class3'].sub( '+', '' )}</span> "
			end
			food_name = res['name']
			if /^\=/ =~ fi
				food_name = fi.sub( '=', '' )
				fi = ''
			end
			return_foods << "<tr><td>#{class_add}#{food_name}</td><td align='right'>#{fuv_v.ceil( 1 )}</td><td align='right'>#{fu}</td></tr>" if res

		end
	end
#	db.close
	return_foods << "</table>"

	return return_foods
end


#### プロトコール変換
def modify_protocol( recipe, user, depth )
	return_protocol = "<ul>\n"
	a = recipe.protocol.split( "\n" )

	c = 1
	a.each do |e|
		if /^\@/ =~ e
			t = e.delete( '@' )
			return_protocol << "<span class='print_comment'>(#{t})</span><br>\n"
		elsif /^\!/ =~ e
			t = e.delete( '!' )
			return_protocol << "<span class='print_subtitle'>#{t}</span><br>\n"
		elsif /^\+/ =~ e
			link_code = e.sub( '+', '' ).chomp
			if recipe.code == link_code || depth > 1
				return_protocol << "<span class='error'>循環参照</span><br>\n"
			else
				ref_recipe = Recipe.new( user )
				recipe_load_flag = ref_recipe.load_db( link_code, true )

				if recipe_load_flag
					local_return_protocol = modify_protocol( ref_recipe, user, depth + 1 )
					local_foods = extract_ref_foods( db, ref_recipe )

					return_protocol << "<div class='accordion' id='accordion#{c}'><div align='right'><a href='printv.cgi?&c=#{link_code}' target='sub_link'><span class='badge bg-info text-dark'>Link</span></a></div>"
					return_protocol << "	<div class='accordion-item'>"
	  			return_protocol << "		<div class='accordion-header' id='heading#{c}'><button class='accordion-button' type='button'  style='padding-top: 0.2rem; padding-bottom: 0.2rem;' data-bs-toggle='collapse' data-bs-target='#collapse#{c}' aria-expanded='true' aria-controls='collapse#{c}'>参照：#{ref_recipe.name}（#{ref_recipe.dish}人分）</button></div>"
	  			return_protocol << "		<div id='collapse#{c}' class='accordion-collapse collapse' aria-labelledby='heading#{c}' data-bs-parent='#accordion#{c}'>"
	    		return_protocol << "			<div class='accordion-body'><div class='row'>"
	    		return_protocol << "	    	<div class='col-7' style='font-size:small'>#{local_return_protocol }</div>"
	    		return_protocol << "	    	<div class='col-5' style='font-size:x-small'>#{local_foods }</div>"
	  			return_protocol << "		</div></div>"
					return_protocol << "	</div>"
					return_protocol << "</div>"
					c += 1
				else
					return_protocol << "<h6>参照レシピ読み込みエラー[#{link_code}]</h6>"
				end
			end
		elsif /^\#/ =~ e
		elsif e == ''
			return_protocol << "<br>\n"
		else
			return_protocol << "<li>#{e}</li>\n"
		end
	end
	return_protocol << "</ul>\n"

	return return_protocol
end


#### 写真構成
def arrange_photo( recipe )
	code = recipe.code
	media_code = recipe.media
	main_photo = ''
#	main_photo = "<a href='#{$PHOTO}/#{media_code[0]}.jpg' target='Photo'><img src='#{$PHOTO}/#{media_code[0]}.jpg' width='100%' height='100%' class='img-thumbnail'></a>\n" if media_code.size > 0
	main_photo = "<img src='#{$PHOTO}/#{media_code[0]}.jpg' width='100%' height='100%' class='img-thumbnail' onclick=\"modalPhoto( '#{media_code[0]}' )\">\n" if media_code.size > 0

	sub_photos = ''
	if media_code.size > 1
		spw = ( 100 / ( media_code.size - 1 )).to_i
		spw = 25 if spw < 25
		1.upto( media_code.size - 1 ) do |c|
#			sub_photos << "<a href='#{$PHOTO}/#{media_code[c]}.jpg' target='Photo'><img src='#{$PHOTO}/#{media_code[c]}-tn.jpg' width='#{spw}%' height='#{spw}%' class='img-thumbnail'></a>\n"
			sub_photos << "<img src='#{$PHOTO}/#{media_code[c]}-tn.jpg' width='#{spw}%' height='#{spw}%' class='img-thumbnail' onclick=\"modalPhoto( '#{media_code[c]}' )\">\n"
		end
	end

	return main_photo, sub_photos
end


#==============================================================================
# Main
#==============================================================================

html_init( nil )

user = User.new( @cgi )
db = Db.new( user, @debug, false )
l = language_pack( user.language )

puts "Getting GET<br>" if @debug
get_data = get_data()
code = get_data['c']
template = get_data['t'].nil? ? 1 : get_data['t'].to_i
dish = get_data['d'].to_i
palette_ = get_data['p'].nil? ? @palette_default_name[1] : CGI.unescape( get_data['p'] )
frct_accu = ( frct_accu == '' || frct_accu == nil )? 1 : frct_accu = frct_accu.to_i
ew_mode = get_data['ew'].to_i
frct_mode = get_data['fm'].to_i
csc = get_data['cs'].to_s


puts "Loading recipe<br>" if @debug
recipe = Recipe.new( user )
recipe.load_db( code, true )
dish = recipe.dish if dish == 0
recipe.load_media
photo_num = recipe.media.size


url = "https://bacura.jp/nb/printv.cgi?c=#{code}&t=#{template}&d=#{dish}&p=#{palette_}"
url << "&cs=#{csc}" unless csc == ''
if @debug
	puts "code: #{code}<br>"
	puts "template: #{template}<br>"
	puts "dish: #{dish}<br>"
	puts "url: #{url}<br>"
	puts "<hr>"
end

puts "html header<br>" if @debug
html_head_pv( recipe, x_account )


puts "extract foods<br>" if @debug
foods = extract_foods( db, recipe, dish, template, ew_mode )
puts "foods: #{foods}<br>" if @debug


puts 'Protocol html<br>' if @debug
protocol = modify_protocol( recipe, user, 0 )


puts 'Photo html<br>' if @debug
main_photo, sub_photos = arrange_photo( recipe )


puts 'Generating QR code<br>' if @debug
makeQRcode( url, code )


puts 'Mode select HTML<br>' if @debug
mode_list = %w( シンプル表示 標準表示 栄養表示 完全栄養表示 )
mode_html = '<div class="input-group input-group-sm">'
mode_html << '<span class="input-group-text">表示モード</span>'
mode_html << "<select class='form-select' name='t'>"
0.upto( 3 ) do |c| mode_html << "<option value='#{c}' #{$SELECT[c== template]}>#{mode_list[c]}</option>" end
mode_html << "</select>"
mode_html << '</div>'


puts 'Palette select HTML<br>' if @debug
palette = Palette.new( user )
palette_ = @palette_default_name[1] if palette_ == nil || palette_ == '' || palette_ == '0'
palette.set_bit( palette_ )
palette_html = '<div class="input-group input-group-sm">'
palette_html << '<span class="input-group-text">栄養パレット</span>'
palette_html << "<select class='form-select' name='p'>"
palette.sets.each_key do |k|
	palette_html << "<option value='#{k}' #{$SELECT[k == palette_]}>#{k}</option>" if palette_ != @palette_default_name[0] || user.name
end
palette_html << "</select>"
palette_html << '</div>'


puts 'FCT Calc<br>' if @debug
fct = FCT.new( user, @fct_item, @fct_name, @fct_unit, @fct_frct, frct_accu, frct_mode )
fct.load_palette( palette.bit )
food_no, food_weight, total_weight = extract_sum( recipe.sum, recipe.dish, ew_mode )
fct.set_food( food_no, food_weight, false )
fct.calc()
fct.digit()


puts 'HTML食品成分表の生成 <br>' if @debug
fct_html = ''
if template >= 2
	table_num = fct.items.size / fct_num
	table_num += 1 if ( fct.items.size % fct_num ) != 0
	fct_width = ( 70 / fct_num ).to_f
	table_num.times do |c|
		fct_html << '<table class="table table-sm">'

		# 項目名
		fct_html << '<tr>'
		if template > 2
			fct_html << '<th width="6%" class="fct_item align_l">食品番号</th>'
			fct_html << '<th width="20%" class="fct_item align_l">食品名</th>'
			fct_html << '<th width="4%" class="fct_item align_r">重量</th>'
		end
		fct_num.times do |cc|
			fct_no = ( c * fct_num ) + cc
			unless fct.names[fct_no] == nil
				fct_html << "<th width='#{fct_width}%' class='fct_item align_r'>#{fct.names[fct_no]}</th>"
			else
				fct_html << "<th width='#{fct_width}%' class='fct_item align_r'></th>"
			end
		end
		fct_html << '</tr>'

		# 単位
		fct_html << '<tr>'
		if template > 2
			fct_html << '<td colspan="2"></td>'
			fct_html << "<td class='fct_unit align_r'>( g )</td>"
		end
		fct_num.times do |cc|
			fct_no = ( c * fct_num ) + cc
			fct_html << "<td class='fct_unit align_r'>( #{fct.units[fct_no]} )</td>" unless fct.units[fct_no] == nil
		end
		fct_html << '</tr>'


		if template > 2
		# 各成分値
			fct.foods.size.times do |cc|
				fct_html << '	<tr>'
				fct_html << "	<td class='align_l'>#{fct.fns[cc]}</td>"
				fct_html << "	<td class='align_l'>#{fct.foods[cc]}</td>"
				fct_html << "	<td class='align_r'>#{fct.weights[cc].to_f}</td>"
				fct_num.times do |ccc|
					fct_no = ( c * fct_num ) + ccc
					fct_html << "	<td class='align_r'>#{fct.solid[cc][fct_no]}</td>" unless fct.solid[cc][fct_no] == nil
				end
				fct_html << '	</tr>'
			end
		end

		# 合計値
		fct_html << '	<tr>'
		if template > 2
			fct_html << '	<td colspan="2" class="fct_sum align_c">合計</td>'
			fct_html << "	<td align='right' class='fct_sum align_r'>#{total_weight.to_f}</td>"
		end
		fct_num.times do |cc|
			fct_no = ( c * fct_num ) + cc
			fct_html << "	<td align='right' class='fct_sum align_r'>#{fct.total[fct_no]}</td>" unless fct.total[fct_no] == nil
		end
		fct_html << '	</tr>'
		fct_html << '</table>'
		fct_html << "<div class='fct_item'>#{frct_select[frct_mode]} / #{accu_check[frct_accu]} / #{ew_check[ew_mode]}</div>\n"
	end
end


nimono = ''
if recipe.tags.include?( "煮物警報" ) && recipe.dish != dish
	if recipe.dish < dish
		nimono = ' <span class="text-danger">▲煮物警報▲</span>　設定人数が元レシピより多いので、煮汁を調節しないと時間がかかったり、味が濃くなるかも！'
	else
		nimono = ' <span class="text-danger">▲煮物警報▲</span>　設定人数が元レシピより少ないので、煮汁を調節しないと火が通らなかったり、味が薄くなるかも！'
	end
end


puts 'Common header <br>' if @debug
html_head = <<-"HTML"
<div class='container'>
	<div class='row'>
		<h4>#{recipe.name}</h4>
		<blockquote>#{recipe.note}</blockquote>
	</div>
	<form action='' method='get'>
	<div class='row' align='center'>
		<div class='col'>
			<div class="input-group input-group-sm">
				<span for="dish_num" class="input-group-text">人数</span>
				<input type='number' name='d' size='3' min='1' value='#{dish}' class="form-control">
			</div>
		</div>
		<div class='col'>
				#{mode_html}
		</div>
		<div class='col'>
				#{palette_html}
		</div>
		<div class='col'>
				<input type='hidden' name='c' value='#{code}'>
				<input type='hidden' name='fa' value='#{frct_accu}'>
				<input type='hidden' name='ew' value='#{ew_mode}'>
				<input type='hidden' name='fm' value='#{frct_mode}'>
				<input type='submit' value='変更' class='btn btn-sm btn-outline-primary'>
		</div>
	</div>
	</form>
	#{nimono}
	<hr>
HTML


puts 'Common footer <br>' if @debug
if csc == ''
	html_foot = <<-"HTML"

	<!-- Modal window -->
	<div class="modal fade" id="modal" tabindex="-1" aria-labelledby="modal_label" aria-hidden="true">
	  <div class="modal-dialog modal-lg">
	    <div class="modal-content">
	      <div class="modal-body" id='modal_body'></div>
	    </div>
	  </div>
	</div>

	<hr>
	<div class='row'>
		<div class='col-6' align="center">
			栄養者の慾を如意自在に同化するユビキタス栄養ツール<br><br>
			<a href='https://bacura.jp/nb/' class='h4 alert alert-danger'>栄養ブラウザ</a>
		</div>
		<div class='col-6' align="center">#{code}<br>
			<img src='#{$PHOTO}/#{code}-qr.png'>
		</div>
	</div>
	<div class='row'>
		<div class='col-5' align="center">#{adsense_printv()}</div>
		<div class='col-5' align="center">#{adsense_printv()}</div>
	</div>
</div>
HTML

else
	res = db.query( "SELECT * FROM #{$TB_SCHOOLC} WHERE code=?", false, [csc] )&.first
	print_ins = ''
	school_name = ''
	qr_ins = ''
	qr_img= ''
	if res
		print_ins = res['print_ins']
		school_name = res['name']
		if res['qr_ins'] != ''
			makeQRcode( res['qr_ins'], csc )
			qr_img = "<img src='#{$PHOTO}/#{csc}-qr.png'>"
		end
	end


	html_foot = <<-"HTML"
	<hr>
	<div class='row'>
		<div class='col-5'>
			<h5>#{school_name}</h5>
			#{print_ins}
		</div>
		<div class='col-2'>
			#{qr_img}
		</div>
		<div class='col-3'>
			<a href='https://nb.bacura.jp/'>栄養ブラウザ</a><br>
			レシピコード：<br>
			<a href='#{url}'>#{code}</a>
		</div>
		<div class='col-2'>
			<img src='#{$PHOTO}/#{code}-qr.png'>
		</div>
	</div>
</div>
HTML
end


case template
#### 基本レシピ / 詳細レシピ
when 0, 1
html = <<-"HTML"
	<div class='row'>
		<div class='col'>
			#{main_photo}
			#{sub_photos}
		</div>
		<div class='col'>
			<h5>材料</h5>
			#{foods}
		</div>
	</div>
	<hr>
	<div class='row'>
		<div class='col'>
			<h5>作り方</h5>
			#{protocol}
		</div>
	</div>
HTML

#### 栄養レシピ
when 2
html = <<-"HTML"
	<div class='row'>
		<div class='col-8'>
			<h5>材料</h5>
			#{foods}
		</div>
		<div class='col-4'>
			#{main_photo}
			#{sub_photos}
		</div>
	</div>
	<hr>
	<div class='row'>
		<div class='col'>
			<h5>作り方</h5>
			#{protocol}
		</div>
	</div>
	<h5>栄養成分</h5>
	#{fct_html}
HTML

#### 完全レシピ
when 3
html = <<-"HTML"
	<div class='row'>
		<div class='col-9'>
			<h5>材料</h5>
			#{foods}
		</div>
		<div class='col-3'>
			#{main_photo}
			#{sub_photos}
		</div>
	</div>
	<hr>
	<div class='row'>
		<div class='col'>
			<h5>作り方</h5>
			#{protocol}
		</div>
	</div>
	<h5>栄養成分</h5>
	#{fct_html}
HTML

end

puts html_head
puts html
puts html_foot
