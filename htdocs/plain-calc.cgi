#! /usr/bin/ruby
#encoding: utf-8
#Nutrition browser 2020 plain calc 0.03b

#==============================================================================
#LIBRARY
#==============================================================================
require './probe'
require './brain'


#==============================================================================
#STATIC
#==============================================================================
script = 'plain-calc'
@debug = false


#==============================================================================
#DEFINITION
#==============================================================================

#### Language init
def lp_init( script, language_set )
  f = open( "#{$HTDOCS_PATH}/language_/#{script}.#{language_set}", "r" )
  lp = [nil]
  f.each do |line| lp << line.chomp.force_encoding( 'UTF-8' ) end
  f.close

  return lp
end


#### 予想重量チェック
def ew_check( ew_mode, lp )
  ew_check = lp[6]
  ew_check = lp[7] if ew_mode == 1

  return ew_check
end


#==============================================================================
# Main
#==============================================================================
puts "Content-type: text/text\n\n"


puts "Extracting SUM data\n" if @debug
get = get_data()
uname = get['uname']
code = get['code']
ew_mode = get['ew_mode']
lg = get_data['lg']

palette_ = ''
if get['palette'] == nil
	palette_ = @palette_default_name[1]
else
	palette_ = CGI.unescape( get['palette'] )
end

ew_mode = 0 if ew_mode == nil
ew_mode = ew_mode.to_i
lg = $DEFAULT_LP if lg = '' || lg = nil
lp = lp_init( script, lg )


puts "Extracting SUM data\n" if @debug
r = mdb( "SELECT code, name, sum, dish from #{$MYSQL_TB_SUM} WHERE user='#{uname}';", false, @debug )
recipe_name = r.first['name']
code = r.first['code']
dish_num = r.first['dish'].to_i
food_no, food_weight, total_weight = extract_sum( r.first['sum'], dish_num, ew_mode )


puts "Checking CHECK\n" if @debug
ew_check = ew_check( ew_mode, lp )


puts "Setting palette\n" if @debug
palette = Palette.new( user )
palette_ = @palette_default_name[1] if palette_ == nil || palette_ == ''
palette.set_bit( palette_ )


puts "FCT Calc\n" if @debug
fct = FCT.new( user, @fct_item, @fct_name, @fct_unit, @fct_frct, 1, 1 )
fct.load_palette( palette.bit )
fct.set_food( food_no, food_weight, false )
fct.calc
#fct.digit


puts "FCT TEXT\n" if @debug
fct_txt = ''

# 項目名
fct_txt << lp[8]
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
	fct_txt << "#{fct.fns[c]}\t#{fct.names[c]}\t#{fct.weights[c].to_f}\t"
	fct.items.size.times do |cc| fct_txt << "#{fct.solid[c][cc].to_f}\t" end
	fct_txt.chop!
	fct_txt << "\n"
end


# 合計値
fct_txt << "\t#{lp[9]}\t#{total_weight.to_f}\t"
fct.total.each do |e|
		fct_txt << "#{e.to_f}\t"
end
fct_txt.chop!
fct_txt << "\n"


#### 食品番号から食品成分を表示
puts "#{lp[10]} #{recipe_name}\t#{lp[11]} #{code}\t#{lp[12]} #{ew_check}\n"
puts fct_txt
