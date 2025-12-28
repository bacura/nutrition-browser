#! /usr/bin/ruby
#encoding: utf-8
#Nutrition browser 2020 plain calc 0.0.3 (2025/12/27)

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
    sgram: "単純g",
    egram: "予想g",
    items: "食品番号	食品名	重量	",
    total: "合計",
    table: "食品成分計算表",
    name: "レシピ名:",
    code: "レシピコード:",
    ugram: "使用重量:"
  }

  return l[language]
end

#==============================================================================
# Main
#==============================================================================
puts "Content-type: text/text\n\n"

user = User.new( @cgi )
db = Db.new( user, @debug, false )

puts "Extracting SUM data\n" if @debug
get = get_data()
uname = get['uname']
code = get['code']
ew_mode = get['ew_mode']
ew_mode = 0 if ew_mode == nil
ew_mode = ew_mode.to_i
lg = get_data['lg']
lg = $DEFAULT_LP if lg.to_s.empty?
l = language_pack( lg )


palette_ = get['palette'].to_s.empty? @palette_default_name.first : CGI.unescape( get['palette'] )


puts "Extracting SUM data\n" if @debug
res = db.query( "SELECT code, name, sum, dish from #{$TB_SUM} WHERE user=?", false, [uname] )&.first
if res
	recipe_name = res['name']
	code = res['code']
	dish_num = res['dish'].to_i
	food_no, food_weight, total_weight = extract_sum( res['sum'], dish_num, ew_mode )
else
	puts 'S(x_x)UM'
	exit
end

puts "Checking CHECK\n" if @debug
ew_check = ew_mode == 1? l[:sgram] : l[:egram]


puts "Setting palette\n" if @debug
palette = Palette.new( user )
palette.set_bit( palette_ )


puts "FCT Calc\n" if @debug
fct = FCT.new( user, @fct_item, @fct_name, @fct_unit, @fct_frct, 1, 1 )
fct.load_palette( palette.bit )
fct.set_food( food_no, food_weight, false )
fct.calc
fct.digit


puts "FCT TEXT\n" if @debug
fct_txt = ''

# 項目名
fct_txt << l[:items]
fct.names.each do |e|
	fct_txt << "#{e}\t"
end
fct_txt.chop!
fct_txt << "\n"

#### 単位
fct_txt << "\t\tg\t"
fct.units.each do |e|
	fct_txt << "#{e}\t"
end
fct_txt.chop!
fct_txt << "\n"


#### 各成分値
fct.foods.size.times do |c|
	fct_txt << "#{fct.fns[c]}\t#{fct.foods_[c]}\t#{fct.weights[c].to_f}\t"
	fct.items.size.times do |cc| fct_txt << "#{fct.solid[c][cc].to_f}\t" end
	fct_txt.chop!
	fct_txt << "\n"
end


# 合計値
fct_txt << "\t#{l[:total]}\t#{total_weight.to_f}\t"
fct.total.each do |e|
		fct_txt << "#{e.to_f}\t"
end
fct_txt.chop!
fct_txt << "\n"


#### 食品番号から食品成分を表示
puts "#{l[:table]}\n#{l[:name]}\t#{recipe_name}\n#{l[:code]}\t#{code}\n#{l[:ugram]}\t#{total_weight.to_f}\t#{ew_check}\n"
puts fct_txt
