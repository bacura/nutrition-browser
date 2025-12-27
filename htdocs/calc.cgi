#! /usr/bin/ruby
#encoding: utf-8
#Nutrition browser magic calc 0.0.9 (2025/02/18)

#==============================================================================
#STATIC
#==============================================================================
@debug = false
myself = File.basename( __FILE__ )
fct_num = 14

#==============================================================================
#LIBRARY
#==============================================================================
require './probe'
require './brain'

#==============================================================================
#DEFINITION
#==============================================================================

# Language pack
def language_pack( language )
	l = Hash.new

	#Japanese
	l['ja'] = {
		calc: 		"食品成分計算表",
		palette:	"パレット",
		precision:	"精密合計",
		ew:			"予想g",
		fract:		"端数",
		round:		"四捨五入",
		ceil:		"切り上げ",
		floor:		"切り捨て",
		food_no:	"食品番号",
		food_name:	"食品名",
		total:		"合計",
		weight:		"重量",
		recalc:		"<img src='bootstrap-dist/icons/calculator.svg' style='height:2em; width:2em;'>",
		raw:		"Raw<img src='bootstrap-dist/icons/download.svg' style='height:1.5em; width:1.5em;'>"
	}

	return l[language]
end

#==============================================================================
# Main
#==============================================================================
html_init( nil )

user = User.new( @cgi )
db = Db.new( user, @debug, false )
l = language_pack( user.language )

r = db.query( "SELECT icalc FROM cfg WHERE user='#{user.name}';", false )
fct_num = r.first['icalc'].to_i unless r.first['icalc'].to_i == 0


#### Getting POST data
command = @cgi['command']
code = @cgi['code']
ew_mode = @cgi['ew_mode']
frct_mode = @cgi['frct_mode']
frct_accu = @cgi['frct_accu']
palette_ = @cgi['palette']

if ew_mode == nil || ew_mode == ''
	r = db.query( "SELECT calcc FROM #{$TB_CFG} WHERE user='#{user.name}';",false )
	if r.first && r.first['calcc'] != nil
		a = r.first['calcc'].split( ':' )
		palette_ = a[0]
		ew_mode = a[1].to_i
		frct_mode = a[2].to_i
		frct_accu = a[3].to_i
	else
		palette_ = nil
		ew_mode = 0
		frct_mode = 1
		frct_accu = 1
	end
end


ew_mode = ew_mode.to_i
frct_mode = frct_mode.to_i
frct_accu = frct_accu.to_i
if @debug
	puts "command: #{command}<br>"
	puts "code: #{code}<br>"
	puts "ew_mode: #{ew_mode}<br>"
	puts "frct_mode: #{frct_mode}<br>"
	puts "frct_accu: #{frct_accu}<br>"
	puts "palette_: #{palette_}<br>"
	puts "<hr>"
end


puts 'Extracting SUM data <br>' if @debug
r = db.query( "SELECT code, name, sum, dish from #{$TB_SUM} WHERE user='#{user.name}';", false )
recipe_name = r.first['name']
code = r.first['code']
food_no, food_weight, total_weight = extract_sum( r.first['sum'], r.first['dish'].to_i, ew_mode )


puts 'Setting palette <br>' if @debug
palette = Palette.new( user )
palette_ = @palette_default_name[1] if palette_ == nil || palette_ == '' || palette_ == '0'
palette.set_bit( palette_ )


puts 'HTMLパレットの生成 <br>' if @debug
palette_html = ''
palette.sets.each_key do |k|
	s = ''
	s = 'SELECTED' if palette_ == k
	palette_html << "<option value='#{k}' #{s}>#{k}</option>"
end


puts 'FCT Calc<br>' if @debug
fct = FCT.new( user, @fct_item, @fct_name, @fct_unit, @fct_frct, frct_accu, frct_mode )
fct.load_palette( palette.bit )
fct.set_food( food_no, food_weight, false )
fct.calc
fct.digit


puts 'HTML食品成分表の生成 <br>' if @debug
fct_html = ''
table_num = fct.items.size / fct_num
table_num += 1 if ( fct.items.size % fct_num ) != 0
fct_width = ( 70 / fct_num ).to_f
table_num.times do |c|
	fct_html << '<table class="table table-striped table-sm">'

	# 項目名
	fct_html << '<tr>'
	fct_html << "	<th align='center' width='6%' class='fct_item'>#{l[:food_no]}</th>"
	fct_html << "	<th align='center' width='20%' class='fct_item'>#{l[:food_name]}</th>"
	fct_html << "	<th align='center' width='4%' class='fct_item'>#{l[:weight]}</th>"
	fct_num.times do |cc|
		fct_no = ( c * fct_num ) + cc
		unless fct.names[fct_no] == nil
			fct_html << "	<th align='center' width='#{fct_width}%' class='fct_item'>#{fct.names[fct_no]}</th>"
		else
			fct_html << "	<th align='center' width='#{fct_width}%' class='fct_item'></th>"
		end
	end
	fct_html << '</tr>'

	# 単位
	fct_html << '<tr>'
	fct_html << '	<td colspan="2" align="center"></td>'
	fct_html << "	<td align='center' class='fct_unit'>( g )</td>"
	fct_num.times do |cc|
		fct_no = ( c * fct_num ) + cc
		fct_html << "	<td align='center' class='fct_unit'>( #{fct.units[fct_no]} )</td>" unless fct.units[fct_no] == nil
	end
	fct_html << '</tr>'

	# 各成分値
	fct.foods.size.times do |cc|
		fct_html << '<tr>'
		fct_html << "	<td align='center'>#{fct.fns[cc]}</td>"
		fct_html << "	<td>#{fct.foods[cc]}</td>"
		fct_html << "	<td align='right'>#{fct.weights[cc].to_f}</td>"
		fct_num.times do |ccc|
			fct_no = ( c * fct_num ) + ccc
			fct_html << "	<td align='right'>#{fct.solid[cc][fct_no]}</td>" unless fct.solid[cc][fct_no] == nil
		end
		fct_html << '</tr>'
	end

	# 合計値
	fct_html << '<tr>'
	fct_html << "	<td colspan='2' align='center' class='fct_sum'>#{l[:total]}</td>"
	fct_html << "	<td align='right' class='fct_sum'>#{total_weight.to_f}</td>"
	fct_num.times do |cc|
		fct_no = ( c * fct_num ) + cc
		fct_html << "	<td align='right' class='fct_sum'>#{fct.total[fct_no]}</td>" unless fct.total[fct_no] == nil
	end
	fct_html << '</tr>'
	fct_html << '</table>'
	fct_html << '<br>'
end

puts 'ダウンロード名設定 <br>' if @debug
if recipe_name != nil && recipe_name != ''
	dl_name = "calc-#{recipe_name}"
elsif code != nil && code != ''
	dl_name = "calc-#{code}"
else
	dl_name = "calc-table"
end


puts 'HTML <br>' if @debug
html = <<-"HTML"
<div class='container-fluid'>
	<div class='row'>
		<div class='col' id='calc'><h5>#{l[:calc]}: #{recipe_name}</h5></div>
	</div>
	<div class="row">
		<div class='col-3'>
			<div class="input-group input-group-sm">
				<label class="input-group-text" for="palette">#{l[:palette]}</label>
				<select class="form-select form-select-sm" id="palette" onchange="recalcView('#{code}')">
					#{palette_html}
				</select>
			</div>
		</div>
		<div class='col-3' align='left'>
			<div class="form-check form-check-inline">
    			<input class="form-check-input" type="checkbox" id="frct_accu" value="1" #{$CHECK[frct_accu]} onchange="recalcView('#{code}')">#{l[:precision]}
			</div>
			<div class="form-check form-check-inline">
    			<input class="form-check-input" type="checkbox" id="ew_mode" value="1" #{$CHECK[ew_mode]} onchange="recalcView('#{code}')">#{l[:ew]}
			</div>
		</div>
		<div class='col-3'>
			<div class="input-group input-group-sm">
				<label class="input-group-text" for="frct_mode">#{l[:fract]}</label>
				<select class="form-select form-select-sm" id="frct_mode" onchange="recalcView('#{code}')">
					<option value="1"#{$SELECT[frct_mode == 1]}>#{l[:round]}</option>
					<option value="2"#{$SELECT[frct_mode == 2]}>#{l[:ceil]}</option>
					<option value="3"#{$SELECT[frct_mode == 3]}>#{l[:floor]}</option>
				</select>
				<span onclick="recalcView('#{code}')">#{l[:recalc]}</span>&nbsp;
			</div>
		</div>

		<div class='col-2'></div>
		<div class='col-1'>
			<a href='plain-calc.cgi?uname=#{user.name}&code=#{code}&palette=#{palette_}&ew_mode=#{ew_mode}' download='#{dl_name}.txt'>#{l[:raw]}</a>
		</div>
    </div>
</div>
<br>
#{fct_html}
<div align='right' class='code'>#{code}</div>

HTML

puts html

#==============================================================================
# POST PROCESS
#==============================================================================

puts 'Updating Calculation option <br>' if @debug
db.query( "UPDATE #{$TB_CFG} SET calcc='#{palette_}:#{ew_mode}:#{frct_mode}:#{frct_accu}' WHERE user='#{user.name}';", true )

#==============================================================================
# FRONT SCRIPT START
#==============================================================================
if command == 'init'
	js = <<-"JS"
<script type='text/javascript'>

var postReqCalc = ( command, data, successCallback ) => {
	$.post( '#{myself}', { command, ...data })
		.done( successCallback )
		.fail(( jqXHR, textStatus, errorThrown ) => {
			console.error( "Request failed: ", textStatus, errorThrown );
			alert( "An error occurred. Please try again." );
		});
};

// 成分計算表の再計算ボタンを押してL2にリストを表示
var recalcView = ( code ) => {
	const palette = $( "#palette" ).val();
	const frct_mode = $( "#frct_mode" ).val();
	const frct_accu = $( "#frct_accu" ).prop( "checked" ) ? 1 : 0;
	const ew_mode   = $( "#ew_mode" ).prop( "checked" ) ? 1 : 0;
	postReqCalc( 'view', { code, palette, frct_mode, frct_accu, ew_mode }, data => $( "#L2" ).html( data ));
};

</script>

JS

	puts js
end
