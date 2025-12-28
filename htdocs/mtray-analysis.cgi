#! /usr/bin/ruby
#encoding: utf-8
#Nutrition browser 2020 food composition analysis for tray 0.0.2 (2025/12/27)

#==============================================================================
#STATIC
#==============================================================================
@debug = false
myself = File.basename( __FILE__ )

#==============================================================================
#LIBRARY
#==============================================================================
require './soul'
require './brain'

#==============================================================================
#DEFINITION
#==============================================================================

#### Language_pack
def language_pack( language )
	l = Hash.new

	#Japanese
	l['ja'] = {
		basic:		"食品構成表（単献立）",
		precision: 	"精密合計",
		weight_ex: 	"予想摂取g",
		fract: 		"端数",
		round: 		"四捨五入",
		round_u:	"切り上げ",
		round_d:	"切り捨て",
		download: 	"Raw<img src='bootstrap-dist/icons/download.svg' style='height:1.5em; width:1.5em;'>",
		compose: 	"食品構成 (g)",
		grains: 	"穀類",
		potato: 	"芋・でん粉類",
		suger:		"砂糖・甘味類",
		beans:		"豆類",
		seeds:	 	"種実類",
		vegitable:	"野菜類",
		gycv: 		"緑黄色野菜",
		wcv: 		"白色野菜",
		fruit: 		"果実類",
		mushroom: 	"きのこ類",
		algae: 		"藻類",
		seafood:	"魚介類",
		meat:	 	"肉類",
		egg: 		"卵類",
		milk: 		"乳類",
		milk_l: 	"液体牛乳",
		milk_p: 	"乳製品",
		fao: 		"油脂類",
		confec: 	"菓子類",
		drink:	 	"嗜好飲料類",
		seasoning: 	"調味料・香辛料類",
		miso: 		"味噌",
		shoyu: 		"醤油",
		salt: 		"食塩",
		others: 	"その他",
		cooked: 	"調理加工食品類",
		total: 		"合計",
		pfc_r: 		"PFC比 (%)",
		protein: 	"たんぱく質 (P)",
		fat: 		"脂質 (F)",
		carboh: 	"炭水化物 (C)",
		grains_er: 	"穀類総エネルギー比 (%)",
		aprotein_er: "動物性たんぱく質比 (%)"
	}

	return l[language]
end

#==============================================================================
# Main
#==============================================================================
html_init( nil )

user = User.new( @cgi )
user.debug if @debug
l = language_pack( user.language )
db = Db.new( user, @debug, false )


puts 'Getting POST <br>' if @debug
command = @cgi['command']
code = @cgi['code']
ew_mode = ( @cgi['ew_mode'] || 0 ).to_i
frct_mode = ( @cgi['frct_mode'] || 0 ).to_i
frct_accu = ( @cgi['frct_accu'] || 0 ).to_i

if @debug
	puts "command: #{command}<br>"
	puts "code: #{code}<br>"
	puts "ew_mode: #{ew_mode}<br>"
	puts "frct_mode: #{frct_mode}<br>"
	puts "frct_accu: #{frct_accu}<br>"
	puts "<hr>"
end


puts 'Preparing calc <br>' if @debug
palette = Palette.new( user )
palette.set_bit( @palette_default_name[1] )

fct = FCT.new( user, @fct_item, @fct_name, @fct_unit, @fct_frct, frct_accu, frct_mode )
fct.load_palette( palette.bit )


puts 'Calculation<br>' if @debug
mt = Tray.new( user )
recipe = Recipe.new( user )
mt.recipes.each do |e|
	recipe.load_db( e, true )
	food_no, food_weight, dummy = extract_sum( recipe.sum, recipe.dish, ew_mode )
	fct.set_food( food_no, food_weight, false )
end
fct.calc
fct.digit


puts 'Counting E<br>' if @debug
animal_protein = BigDecimal( 0 )
grain_energy = BigDecimal( 0 )
fct.fns.each.with_index do |e, i|
	fg = e.sub( /[PUC]/, '' ).slice( 0, 2 ).to_i
	# 動物性たんぱく質カウント
	animal_protein += fct.solid[i][1] if fg >= 10 && fg <= 13
	# 穀類エネルギーカウント
	grain_energy += fct.solid[i][0] if fg == 1
end


puts 'Counting food composition<br>' if @debug
fch = Hash[ ('00'..'18').map do |key| [key, 0] end ]
wcv = 0
gycv = 0
milk_liquid = 0
milk_product = 0
salt = 0
miso = 0
shoyu = 0
seasoning = 0

fct.fns.each.with_index do |e, i|
	food_group = e.sub( /[PUC]/, '' ).slice( 0, 2 )
	fch[food_group] += fct.weights[i]

	case food_group
	when '06'
		# 緑黄色野菜の判定
		res = db.query( "SELECT gycv FROM #{$TB_EXT} WHERE FN=?", false, [e] )&.first
		if res['gycv'] == 1
			gycv += fct.weights[i]
		else
			wcv += fct.weights[i]
		end
	when '13'
		# 牛乳と乳製品の判定
		if e.to_i >= 13001 && e.to_i <= 13006
			milk_liquid += fct.weights[i]
		else
			milk_product += fct.weights[i]
		end
	when '17'
		# 液体だしの乾燥重量化
		if e.to_i >= 17019 && e.to_i <= 17025
			fct.weights[i] = fct.weights[i] / 100 * 1.0
		elsif e.to_i == 17026
			fct.weights[i] = fct.weights[i] / 100 * 2.5
		end
		# 塩の判定
		if ( e.to_i >= 17012 && e.to_i <= 17014 ) || e.to_i == 17089
			salt += fct.weights[i]
		# 味噌の判定
		elsif ( e.to_i >= 17044 && e.to_i <= 17050 ) || e.to_i == 17119 || e.to_i == 17120
			miso += fct.weights[i]
		# 醤油の判定
		elsif ( e.to_i >= 17007 && e.to_i <= 17011 ) || ( e.to_i >= 17086 && e.to_i <= 17088 )
			shoyu += fct.weights[i]
		else
			seasoning += fct.weights[i]
		end
	end
end


puts 'Getting PFC rate<br>' if @debug
pfc = fct.calc_pfc


puts 'Animal protein rate<br>' if @debug
animal_protein_rate = ( animal_protein / fct.total[1] * 100 ).round( 1 )


puts 'Grain energy rate<br>' if @debug
grain_energy_rate = ( grain_energy / fct.total[0] * 100 ).round( 1 )


puts 'Download name<br>' if @debug
if mt.name && !mt.name.empty?
	dl_name = "analysis-#{mt.name}"
elsif code && !code.empty?
	dl_name = "analysis-#{code}"
else
	dl_name = "analysis-table"
end


puts 'HTML <br>' if @debug
html = <<-"HTML"
<div class='container-fluid'>
	<div class='row'>
		<div class='col'><h5>#{l[:basic]}: #{mt.name}</h5></div>
	</div>
	<div class="row">
		<div class='col-4' align='center'>
			<div class="form-check form-check-inline">
    			<input class="form-check-input" type="checkbox" id="frct_accu" value="1" #{$CHECK[frct_accu]} onchange="RecalcMTAnalysis('#{code}')">#{l[:precision]}
			</div>
			<div class="form-check form-check-inline">
    			<input class="form-check-input" type="checkbox" id="ew_mode" value="1" #{$CHECK[ew_mode]} onchange="RecalcMTAnalysis('#{code}')">#{l[:weight_ex]}
			</div>
		</div>
		<div class='col-3'>
			<div class="input-group input-group-sm">
				<label class="input-group-text" for="">#{l[:fract]}</label>
				<select class="form-select" id="frct_mode" onchange="RecalcMTAnalysis('#{code}')">
					<option value="1"#{$SELECT[frct_mode == 1]}>#{l[:round]}</option>
					<option value="2"#{$SELECT[frct_mode == 2]}>#{l[:round_u]}</option>
					<option value="3"#{$SELECT[frct_mode == 3]}>#{l[:round_d]}</option>
				</select>
			</div>
		</div>

		<div class='col-4'></div>
		<div class='col-1'>
			<a href='mtray-analysis-txt.cgi?uname=#{user.name}&code=#{code}&ew_mode=#{ew_mode}' download='#{dl_name}.txt'>#{l[:download]}</a>
		</div>
    </div>
</div>
<br>
<div class='table-responsive-sm'>
	<table class="table table-bordered table-sm">
		<tbody>
		<tr><th width="20%" rowspan='24'>#{l[:compose]}</th><th width="25%">#{l[:grains]}</th><td width="15%">#{fch['01'].to_f}</td></tr>
		<tr><th>#{l[:potato]}</th><td>#{fch['02'].to_f}</td></tr>
		<tr><th>#{l[:suger]}</th><td>#{fch['03'].to_f}</td></tr>
		<tr><th>#{l[:beans]}</th><td>#{fch['04'].to_f}</td></tr>
		<tr><th>#{l[:seeds]}</th><td>#{fch['05'].to_f}</td></tr>
		<tr><th rowspan="2">#{l[:vegitable]}</th><td rowspan="2">#{fch['06'].to_f}</td><th width="25%">#{l[:gycv]}</th><td>#{gycv.to_f}</td></tr>
				<tr><th>#{l[:wcv]}</th><td>#{wcv.to_f}</td></tr>
		<tr><th>#{l[:fruit]}</th><td>#{fch['07'].to_f}</td></tr>
		<tr><th>#{l[:mushroom]}</th><td>#{fch['08'].to_f}</td></tr>
		<tr><th>#{l[:algae]}</th><td>#{fch['09'].to_f}</td></tr>
		<tr><th>#{l[:seafood]}</th><td>#{fch['10'].to_f}</td></tr>
		<tr><th>#{l[:meat]}</th><td>#{fch['11'].to_f}</td></tr>
		<tr><th>#{l[:egg]}</th><td>#{fch['12'].to_f}</td></tr>
		<tr><th rowspan="2">#{l[:milk]}</th><td rowspan="2">#{fch['13'].to_f}</td><th>#{l[:milk_l]}</th><td>#{milk_liquid.to_f}</td></tr>
				<tr><th>#{l[:milk_p]}</th><td>#{milk_product.to_f}</td></tr>
		<tr><th>#{l[:fao]}</th><td>#{fch['14'].to_f}</td></tr>
		<tr><th>#{l[:confec]}</th><td>#{fch['15'].to_f}</td></tr>
		<tr><th>#{l[:drink]}</th><td>#{fch['16'].to_f}</td></tr>
		<tr><th rowspan="4">#{l[:seasoning]}</th><td rowspan="4">#{fch['17'].to_f}</td><th>#{l[:miso]}</th><td>#{miso.to_f}</td></tr>
			<tr><th>#{l[:shoyu]}</th><td>#{shoyu.to_f}</td></tr>
			<tr><th>#{l[:salt]}</th><td>#{salt.to_f}</td></tr>
			<tr><th>#{l[:others]}</th><td>#{seasoning.to_f}</td></tr>
		<tr><th>#{l[:cooked]}</th><td>#{fch['18'].to_f}</td></tr>
		<tr><th>#{l[:total]}</th><td>#{fct.total_weight.to_f}</td></tr>
		<tr><th rowspan='3'>#{l[:pfc_r]}</th><th>#{l[:protein]}</th><td>#{pfc[0].to_f}</td></tr>
			<th>#{l[:fat]}</th><td>#{pfc[1].to_f}</td></tr>
			<th>#{l[:carboh]}</th><td>#{pfc[2].to_f}</td></tr>
		<tr><th rowspan='2'>#{l[:others]}</th><th>#{l[:grains_er]}</th><td>#{grain_energy_rate.to_f}</td></tr>
			<th>#{l[:aprotein_er]}</th><td>#{animal_protein_rate.to_f}</td></tr>
		</tbody>
	</table>
</div>
HTML

puts html
puts "<div align='right' class='code'>#{code}</div>"

#==============================================================================
# POST PROCESS
#==============================================================================


#==============================================================================
# FRONT SCRIPT START
#==============================================================================
if command == 'init'
	js = <<~JS
<script type='text/javascript'>

// Reanalysis of menu
var RecalcMTAnalysis = ( code ) => {
	const frct_mode = document.getElementById( 'frct_mode' ).value;
	const frct_accu = document.getElementById( 'frct_accu' ).checked ? 1 : 0;
	const ew_mode = document.getElementById( 'ew_mode' ).checked ? 1 : 0;

	postLayer( '#{myself}', 'recalc', true, 'L2', { code, frct_mode, frct_accu, ew_mode });
	
	displayVIDEO( 'Reanalysis' );
};

</script>

JS

	puts js
end

puts '(^q^)' if @debug
