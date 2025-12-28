#! /usr/bin/ruby
#encoding: utf-8
#Nutrition browser 2020 menu basic analysis 0.0.2 (2025/12/28)

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
		name: 	"献立名：",
		code: 	"献立コード：",
		weight_mode: 	"重量モード：",
		agram: 	"単純g",
		egram: 	"予想g",
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
puts "Content-type: text/text\n\n"

user = User.new( @cgi )
db = Db.new( user, @debug, false )

#### GETデータの取得
get = get_data()
code = get['code']
ew_mode = get['ew_mode']
ew_mode = 0 if ew_mode == nil
ew_mode = ew_mode.to_i
lg = get_data['lg']
lg = $DEFAULT_LP if lg.to_s.empty?
l = language_pack( lg )


puts "Checking CHECK" if @debug
ew_check = ew_mode == 1 ? l[:sgram] : l[:egram]


puts "Setting palette" if @debug
palette = Palette.new( user )
palette_ = get['palette'].to_s.empty? ? @palette_default_name.first : CGI.unescape( get['palette'] )
palette.set_bit( palette_ )

fct = FCT.new( user, @fct_item, @fct_name, @fct_unit, @fct_frct, 1, 1 )
fct.load_palette( palette.bit )


puts "Calculation" if @debug
mt = Tray.new( user )
recipe = Recipe.new( user )
mt.recipes.each do |e|
	recipe.load_db( e, true )
	food_no, food_weight, dummy = extract_sum( recipe.sum, recipe.dish, ew_mode )
	fct.set_food( food_no, food_weight, false )
end
fct.calc
fct.digit


puts "Counting E" if @debug
animal_protein = BigDecimal( 0 )
grain_energy = BigDecimal( 0 )
fct.fns.each.with_index do |e, i|
	fg = e.sub( /[PUC]/, '' ).slice( 0, 2 ).to_i
	# 動物性たんぱく質カウント
	animal_protein += fct.solid[i][1] if fg >= 10 && fg <= 13
	# 穀類エネルギーカウント
	grain_energy += fct.solid[i][0] if fg == 1
end


puts "Counting food group" if @debug
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


puts 'Getting PFC rate' if @debug
pfc = fct.calc_pfc


puts "Animal protein rate" if @debug
animal_protein_rate = ( animal_protein / fct.total[1] * 100 )


puts 'Grain energy rate' if @debug
grain_energy_rate = ( grain_energy / fct.total[0] * 100 )


puts 'Generatin txt' if @debug
analysis_text = ''
analysis_text << "#{l[:compose]}\t#{l[:grains]}\t#{fch['01'].to_f}\n"
analysis_text << "\t#{l[:potato]}\t#{fch['02'].to_f}\n"
analysis_text << "\t#{l[:suger]}\t#{fch['03'].to_f}\n"
analysis_text << "\t#{l[:beans]}\t#{fch['04'].to_f}\n"
analysis_text << "\t#{l[:seeds]}\t#{fch['05'].to_f}\n"
analysis_text << "\t#{l[:vegitable]}\t#{fch['06'].to_f}\n"
analysis_text << "\t#{l[:gycv]}\t#{gycv.to_f}\n"
analysis_text << "\t#{l[:wcv]}\t#{wcv.to_f}\n"
analysis_text << "\t#{l[:fruit]}\t#{fch['07'].to_f}\n"
analysis_text << "\t#{l[:mushroom]}\t#{fch['08'].to_f}\n"
analysis_text << "\t#{l[:algae]}\t#{fch['09'].to_f}\n"
analysis_text << "\t#{l[:seafood]}\t#{fch['10'].to_f}\n"
analysis_text << "\t#{l[:meat]}\t#{fch['11'].to_f}\n"
analysis_text << "\t#{l[:egg]}\t#{fch['12'].to_f}\n"
analysis_text << "\t#{l[:milk]}\t#{fch['13'].to_f}\n"
analysis_text << "\t#{l[:milk_l]}\t#{milk_liquid.to_f}\n"
analysis_text << "\t#{l[:milk_p]}\t#{milk_product.to_f}\n"
analysis_text << "\t#{l[:fao]}\t#{fch['14'].to_f}\n"
analysis_text << "\t#{l[:confec]}\t#{fch['15'].to_f}\n"
analysis_text << "\t#{l[:drink]}\t#{fch['16'].to_f}\n"
analysis_text << "\t#{l[:seasoning]}\t#{fch['17'].to_f}\n"
analysis_text << "\t#{l[:miso]}\t#{miso.to_f}\n"
analysis_text << "\t#{l[:shoyu]}\t#{shoyu.to_f}\n"
analysis_text << "\t#{l[:salt]}\t#{salt.to_f}\n"
analysis_text << "\t#{l[:others]}\t#{seasoning.to_f}\n"
analysis_text << "\t#{l[:cooked]}\t#{fch['18'].to_f}\n"
analysis_text << "\t#{l[:total]}\t#{fct.total_weight.to_f}\n"
analysis_text << "#{l[:pfc_r]}\t#{l[:protein]}\t#{pfc[0].to_f}\n"
analysis_text << "\t#{l[:fat]}\t#{pfc[1].to_f}\n"
analysis_text << "\t#{l[:carboh]}\t#{pfc[2].to_f}\n"
analysis_text << "#{l[:others]}\t#{l[:grains_er]}\t#{grain_energy_rate.to_f}\n"
analysis_text << "\t#{l[:aprotein_er]}\t#{animal_protein_rate.to_f}\n"

puts 'Output txt' if @debug
puts "#{l[:basic]}"
puts "#{l[:name]}\t#{mt.name}"
puts "#{l[:code]}\t#{mt.code}"
puts "#{l[:weight_mode]}\t#{ew_check}"
puts analysis_text
