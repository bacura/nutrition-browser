#! /usr/bin/ruby
#encoding: utf-8
#Nutrition browser 2020 plain menu calc 0.0.3 (2025/12/27)

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

# Language pack
def language_pack( language )
  l = Hash.new

  #Japanese
  l['ja'] = {
    table: "食品成分計算表（献立）",
    menu_name: "献立名:",
    code: "献立コード：",
    food_no: "食品番号",
    food_name: "食品名",
    weight: "重量",
		sub_total: 	'小計',
		palette: 	'パレット',
		weight_mode: 	'重量モード',
    egram: "予想g",
    gram: "単純g",
		round: 		'四捨五入',
    ceil: "切り上げ",
    floor: "切り捨て",
		total: 		'合計'
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


puts "Checking CHECK\n" if @debug
ew_check = ew_mode == 1 ? l[:sgram] : l[:egram]


puts "Setting palette\n" if @debug
palette = Palette.new( user )
palette_ = get['palette'].to_s.empty? ? @palette_default_name.first : CGI.unescape( get['palette'] )
palette.set_bit( palette_ )

total_fct = FCT.new( user, @fct_item, @fct_name, @fct_unit, @fct_frct, 1, 1 )
total_fct.load_palette( palette.bit )


puts 'Each FCT Calc<br>' if @debug
rc = 0
recipe_name = []
fct_txt = []
total_total_weight = 0

mt = Tray.new( user )
mt.recipes.each do |e|
	p e if @debug
	res = db.query( "SELECT name, sum, dish from #{$TB_RECIPE} WHERE code=?", false, [e] )&.first
	if res
		recipe_name[rc] = res['name']
		dish_num = res['dish'].to_i
		dish_num = 1 if dish_num == 0
		food_no, food_weight, total_weight = extract_sum( res['sum'], dish_num, ew_mode )
		total_total_weight += total_weight
	end

	fct = FCT.new( user, @fct_item, @fct_name, @fct_unit, @fct_frct, 1, 1 )
	fct.load_palette( palette.bit )
	fct.set_food( food_no, food_weight, false )
	fct.calc
	fct.digit

	total_fct.into_solid( fct.total )

	puts "Generating Food Table\n" if @debug
	fct_txt[rc] = ''
	puts "Items\n" if @debug
	fct_txt[rc] << "#{recipe_name[rc]}\t#{l[:food_no]}\t#{l[:food_name]}\t#{l[:weight]}"
	fct.names.each do |ee| fct_txt[rc] << "\t#{ee}" end
	fct_txt[rc] << "\n"

	puts "Units\n" if @debug
	fct_txt[rc] << "\t\t\t(g)"
	fct.units.each do |ee| fct_txt[rc] << "\t(#{ee})" end
	fct_txt[rc] << "\n"

	puts "FCTs\n" if @debug
	fct.foods.size.times do |c|
			fct_txt[rc] << "\t#{fct.fns[c]}\t#{fct.foods_[c]}\t#{fct.weights[c].to_f}"
			fct.items.size.times do |cc|
				fct_txt[rc] << "\t#{fct.solid[c][cc].to_f}"
			end
			fct_txt[rc] << "\n"
	end

	puts "Sub total\n" if @debug
	fct_txt[rc] << "\t\t#{l[:sub_total]}\t#{total_weight.to_f}"
	fct.total.each do |e| fct_txt[rc] << "\t#{e.to_f}" end
	fct_txt[rc] << "\n\n"

	rc += 1
end
total_fct.calc
total_fct.digit


#### HTML食品成分全合計
fct_txt_sum = ''

puts "Total items\n" if @debug
fct_txt_sum << "\t\t\t#{l[:weight]}\t"
total_fct.names.each do |e| fct_txt_sum << "#{e}\t" end
fct_txt_sum.chop!
fct_txt_sum << "\n"

puts "Total units\n" if @debug
fct_txt_sum << "\t\t\t(g)\t"
total_fct.units.each do |e| fct_txt_sum << "(#{e})\t" end
fct_txt_sum.chop!
fct_txt_sum << "\n"

puts "Total total\n" if @debug
fct_txt_sum << "\t\t#{l[:total]}\t#{total_total_weight.to_f}\t"
total_fct.total.each do |e| fct_txt_sum << "#{e.to_f}\t" end
fct_txt_sum.chop!
fct_txt_sum << "\n"

puts "Output txt\n" if @debug
puts "#{l[:table]}\n#{l[:menu_name]}\t#{mt.name}\n#{l[:code]}\t#{mt.code}\n#{l[:weight_mode]}\t#{ew_check}\n"
fct_txt.each do |e| puts e end
puts fct_txt_sum
