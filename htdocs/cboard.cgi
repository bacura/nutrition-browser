#! /usr/bin/ruby
#encoding: utf-8
#Nutrition browser 2020 cutting board 0.4.1 (2025/04/01)

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
	l['jp'] = {
		'cboard' 	=> "まな板",\
		'dish' 		=> "食数",\
		'fn' 		=> "食品#",\
		'chomi' 	=> "調味％",\
		'guide_g' 	=> "目安g",\
		'guide_e' 	=> "目安E",\
		'guide_s' 	=> "目安塩",\
		'waste' 	=> "残食g",\
		'gram' 		=> "g/人",\
		'reset' 	=> "お片付け",\
		'operation' => "操作",\
		'food_name' => "食品名",\
		'memo' 		=> "一言メモ",\
		'simple_g' 	=> "単純g",\
		:chomi_pub 	=> '公開含む',\
		'sort' 		=> "<img src='bootstrap-dist/icons/sort-down.svg' style='height:1.2em; width:1.2em;'>",\
		'expect_g' 	=> "予想g",\
		'volume' 	=> "量",\
		'unit' 		=> "単位",\
		'rrate' 	=> "摂食率",\
		'up' 		=> "<img src='bootstrap-dist/icons/chevron-up.svg' style='height:1.5em; width:1.5em;'>",\
		'down' 		=> "<img src='bootstrap-dist/icons/chevron-down.svg' style='height:1.5em; width:1.5em;'>",\
		'eraser' 	=> "<img src='bootstrap-dist/icons/eraser.svg' style='height:1.8em; width:1.8em;'>",\
		'recipe'	=> "レシピ",\
		'calc' 		=> "栄養",\
		'price' 	=> "原価",\
		'lucky' 	=> "Lucky☆",\
		'foodize' 	=> "食品化",\
		'detective' => "名探偵",\
		'save' 		=> "<img src='bootstrap-dist/icons/save.svg' style='height:1.8em; width:1.8em;'>",\
		'printer'	=> "<img src='bootstrap-dist/icons/printer.svg' style='height:1.8em; width:1.8em;'>"
	}

	return l[language]
end

#### Easy weight calc
def weight_calc( food_list, dish_num, adjew )
	weight = BigDecimal( '0' )
	weight_checked = BigDecimal( '0' )

	check_all = true
	food_list.each do |e|
		check_all = false if e.check == '1'
	end

	food_list.each do |e|
		unless e.fn == '-' || e.fn == '+'
			rr = 1.0
			rr = e.rr.to_f if adjew == 1
			weight_ = BigDecimal( e.weight.to_s ) * rr
			weight += weight_
			weight_checked += weight_ if e.check == '1' || check_all
		end
	end

	weight = ( weight / dish_num.to_i )
	weight_checked = ( weight_checked / dish_num.to_i )

	return weight, weight_checked, check_all
end


#### Easy energy calc
def energy_calc( food_list, dish_num, adjew, db )
	energy = BigDecimal( '0' )
	energy_checked = BigDecimal( '0' )

	check_all = true
	food_list.each do |e|
		check_all = false if e.check == '1'
	end

	food_list.each do |e|
		unless e.fn == '-' || e.fn == '+'
			q = "SELECT ENERC_KCAL from #{$MYSQL_TB_FCT} WHERE FN='#{e.fn}';"
			q = "SELECT ENERC_KCAL from #{$MYSQL_TB_FCTP} WHERE FN='#{e.fn}' AND ( user='#{db.user.name}' OR user='#{$GM}' );" if /P|U/ =~ e.fn
			r = db.query( q, false )
			if r.first
				rr = 1.0
				rr = e.rr.to_f if adjew == 1
				weight_ = BigDecimal( e.weight.to_s ) * rr
				t = BigDecimal( convert_zero( r.first['ENERC_KCAL'] ))
				energy += ( t * weight_ / 100 )
				energy_checked += ( t * weight_ / 100 ) if e.check == '1' || check_all
			end
		end
	end
	energy = ( energy / dish_num.to_i )
	energy_checked = ( energy_checked / dish_num.to_i )

	return energy, energy_checked, check_all
end


#### Easy salt calc
def salt_calc( food_list, dish_num, adjew, db )
	salt = BigDecimal( '0' )
	salt_checked = BigDecimal( '0' )

	check_all = true
	food_list.each do |e|
		check_all = false if e.check == '1'
	end

	food_list.each do |e|
		unless e.fn == '-' || e.fn == '+'
			q = "SELECT NACL_EQ from #{$MYSQL_TB_FCT} WHERE FN='#{e.fn}';"
			q = "SELECT NACL_EQ from #{$MYSQL_TB_FCTP} WHERE FN='#{e.fn}' AND ( user='#{db.user.name}' OR user='#{$GM}' );" if /P|U/ =~ e.fn
			r = db.query( q, false )
			if r.first
				rr = 1.0
				rr = e.rr.to_f if adjew == 1
				weight_ = BigDecimal( e.weight.to_s ) * rr
				t = BigDecimal( convert_zero( r.first['NACL_EQ'] ))
				salt += ( t * weight_ / 100 )
				salt_checked += ( t * weight_ / 100 ) if e.check == '1' || check_all
			end
		end
	end
	salt = ( salt / dish_num.to_i )
	salt_checked = ( salt_checked / dish_num.to_i )

	return salt, salt_checked, check_all
end


#### Processing weight fraction
def proc_wf( weight )
	negative = false
	if weight < 0
		negative = true
		weight *= -1
	end

	weight_ = BigDecimal( 0 )
	if weight <= 0.01
		weight_ = 0.01
	elsif weight >= 0.01 && weight < 0.10
		weight_ = weight.round( 2 )

	elsif weight >= 0.10 && weight < 0.5
		weight_ = weight.round( 2 )
	elsif weight >= 0.5 && weight < 1.0
		weight_ = weight.floor( 1 )
		t = weight - weight_
		if t >= 0.075
			weight_ += 0.1
		elsif t >= 0.025 && t > 0.075
			weight_ += 0.05
		end

	elsif weight >= 1.0 && weight < 5.0
		weight_ = weight.round( 1 )
	elsif weight >= 5 && weight < 10
		weight_ = weight.floor( 0 )
		t = weight - weight_
		if t >= 0.75
			weight_ += 1
		elsif t >= 0.25 && t > 0.75
			weight_ += 0.5
		end

	elsif weight >= 10 && weight < 50
		weight_ = weight.round( 0 )
	elsif weight >= 50 && weight < 100
		weight_ = weight.floor( -1 )
		t = weight - weight_
		if t >= 7.5
			weight_ += 10
		elsif t >= 2.5 && t > 7.5
			weight_ += 5
		end

	elsif weight >= 100 && weight < 500
		weight_ = weight.round( -1 )
	elsif weight >= 500
		weight_ = weight.floor( -2 )
		t = weight - weight_
		if t >= 75
			weight_ += 100
		elsif t >= 25 && t > 75
			weight_ += 50
		end
	end

	weight_ *= -1 if negative

	return weight_
end


#### Chomi cell
def chomi_cell( l, code, chomi_selected, chomi_code, chomi_pub, db )
	puts 'chomi % categoty set<br>' if @debug
	chomi_html = ''
	chomim_categoty = []

	sql_chomi_pub = chomi_pub == 1 ? "OR public='1'" : ''
	r = db.query( "SELECT code, name FROM #{$MYSQL_TB_RECIPE} WHERE ( user='#{db.user.name}' #{sql_chomi_pub} ) and role='100' ORDER BY name;", false )
	r.each do |e|
		a = e['name'].sub( '：', ':' ).split( ':' )
		chomim_categoty << a[0]
	end

	chomim_categoty.uniq!

	chomi_html << '<div class="input-group input-group-sm">'
	chomi_html << "<input type=\"hidden\" value=\"#{code}\" id=\"recipe_code\">"

	if chomi_selected != '' && chomi_selected != nil
		chomi_html << "<button type=\"button\" class=\"btn btn-outline-primary btn-sm\" onclick=\"chomiAdd( '#{code}' )\">#{l['chomi']}</button>"
	else
		chomi_html << "<button type=\"button\" class=\"btn btn-secondary btn-sm\">#{l['chomi']}</button>"
	end

	chomi_html << "<select class=\"form-select\" id=\"chomi_selected\" onchange=\"chomiSelect()\">"
	chomi_html << "<option value=\"\">-</option>"
	chomim_categoty.each do |e|
		chomi_html << "<option value=\"#{e}\" #{$SELECT[chomi_selected == e]}>#{e}</option>"
	end
	chomi_html << "</select>"

	puts 'chomi % code set<br>' if @debug
	chomi_html << "<select class=\"form-select\" id=\"chomi_code\">"
	r.each do |e|
		a = e['name'].sub( '：', ':' ).split( ':' )
		if chomi_selected == a[0]
			chomi_html << "<option value=\"#{e['code']}\" #{$SELECT[chomi_code == e['code']]}>#{a[1]}</option>"
		end
	end
	chomi_html << "</select>"
	chomi_html << "</div>"

	return chomi_html
end


#==============================================================================
# Main
#==============================================================================
html_init( nil )

user = User.new( @cgi )
db = Db.new( user, @debug, false )
cfg = Config.new( user, 'cboard' )
l = language_pack( user.language )

#### POST
command = @cgi['command']
order = @cgi['order']
dish_num = @cgi['dish_num']
fn = @cgi['fn']
food_init_ = @cgi['food_init']
food_rr_ = @cgi['food_rr']
food_check = @cgi['food_check']
unitv = @cgi['unitv']
unit= @cgi['unit']
code = @cgi['code']
chomi_selected = @cgi['chomi_selected']
chomi_code = @cgi['chomi_code']
chomi_pub = @cgi['chomi_pub']
recipe_user = @cgi['recipe_user']
recipe_user = user.name if recipe_user == nil || recipe_user == ''
if @debug
	puts "command:#{command}<br>"
	puts "code:#{code}<br>"
	puts "order:#{order}<br>"
	puts "dish_num:#{dish_num}<br>"
	puts "fn:#{fn}<br>"
	puts "food_init_:#{food_init_}<br>"
	puts "food_rr_:#{food_rr_}<br>"
	puts "food_check:#{food_check}<br"
	puts "unit:#{unit}<br>"
	puts "unitv:#{unitv}<br>"
	puts "chomi_selected:#{chomi_selected}<br>"
	puts "chomi_code:#{chomi_code}<br>"
	puts "chomi_pub:#{chomi_pub}<br>"
	puts "recipe_user:#{recipe_user}<br>"
#	puts "adjew:#{adjew}<br>"
	puts "<hr>"
end

puts "Loading Config<br>" if @debug
chomi_pub = chomi_pub.to_s.empty? ? cfg.val['chomi_pub'].to_i : chomi_pub.to_i


puts "Loading Sum<br>" if @debug
if command == 'load'
	query = "SELECT * from #{$MYSQL_TB_RECIPE} WHERE user='#{recipe_user}' AND code='#{code}';"
else
	query = "SELECT * from #{$MYSQL_TB_SUM} WHERE user='#{user.name}';"
end
r = db.query( query, false )
code = r.first['code']
recipe_name = r.first['name']
recipe_user = r.first['user']
dish_num = r.first['dish'].to_i if dish_num == '' || dish_num == nil
dish_num = 1 if dish_num == 0
protect = r.first['protect'].to_i
adjew = 0
adjew = r.first['adjew'].to_i if command != 'load' && command != 'adjew'

sum = r.first['sum']
sum = '' if sum == nil
food_list = []
sum.split( "\t" ).each do |e|
	t = Sum.new( user )
	t.load_sum( e )
	food_list << t
end
if @debug
	puts "code:#{code}<br>"
	puts "recipe_name:#{recipe_name}<br>"
	puts "dish_num:#{dish_num}<br>"
	puts "protect:#{protect}<br>"
	puts "sum:#{sum}<br>"
	puts "food_list:#{food_list}<br>"
	puts "<hr>"
end


#### adjust weight mode
adjew_checked = [ '', 'CHECKED' ]
r = db.query( "SELECT calcc FROM #{$MYSQL_TB_CFG} WHERE user='#{user.name}';",false )
if r.first && r.first['calcc'] != nil
	a = r.first['calcc'].split( ':' )
	palette_ = a[0]
	adjew = a[1].to_i
	frct_mode = a[2].to_i
	frct_accu = a[3].to_i
else
	palette_ = nil
	frct_mode = 1
	frct_accu = 1
end
if command == 'adjew'
	puts "Adjust mode<br>" if @debug
	adjew = @cgi['adjew'].to_i
	db.query( "UPDATE #{$MYSQL_TB_CFG} SET calcc='#{palette_}:#{adjew}:#{frct_mode}:#{frct_accu}' WHERE user='#{user.name}';", true )
end

update = ''
all_check = ''
case command
when 'chomi_cell'
	chomi_html = chomi_cell( l, code, chomi_selected, chomi_code, chomi_pub, db )
	puts chomi_html
	exit

when 'clear'
	puts "Clear Sum<br>" if @debug
	# まとめて削除
	if food_check== 'all'
		food_list = []
		recipe_name = ''
		code = ''
		dish_num = 1


	# 1つずつ削除
	else
		food_list.delete_at( order.to_i )
		update = '*'
	end

when 'upper'
	puts "Uppser Sum<br>" if @debug
	if food_list[order.to_i].check == '1'
		if order.to_i == 0
			t = food_list.shift
			food_list << t
		else
			target_food = 0
			0.upto( order.to_i - 1 ) do |c|
				target_food = c + 1 if food_list[c].check == '1'
			end

			t = food_list.delete_at( order.to_i )
			food_list.insert( target_food, t )
		end
	else
		if order.to_i == 0
			t = food_list.shift
			food_list << t
		else
			t = food_list.delete_at( order.to_i )
			food_list.insert( order.to_i - 1, t )
		end
	end
	update = '*'

when 'lower'
	puts "Lower Sum<br>" if @debug
	if food_list[order.to_i].check == '1'
		if order.to_i == food_list.size - 1
			t = food_list.pop
			food_list.unshift( t )
		else
			target_food = food_list.size - 1
			( food_list.size - 1 ).downto( order.to_i + 1 ) do |c|
				target_food = c - 1 if food_list[c].check == '1'
			end

			t = food_list.delete_at( order.to_i )
			food_list.insert( target_food, t )
		end
	else
		if order.to_i == food_list.size - 1
			t = food_list.pop
			food_list.unshift( t )
		else
			t = food_list.delete_at( order.to_i )
			food_list.insert( order.to_i + 1, t )
		end
	end
	update = '*'

when 'sort'
	puts "Sorting list by food weight<br>" if @debug
	bs_set = []
	so_set = []
	as_set = []
	check_flag = false
	food_list.each do |e|
		check_flag = true if e.check == '1'
		if check_flag
			if e.check == '1'
			#sorting
				so_set << e
			else
			#after sorting
				as_set << e
			end
		else
		#Before sorting
			bs_set << e
		end
	end

	unless check_flag
		so_set = Marshal.load( Marshal.dump( bs_set ))
		bs_set = []
	end
	so_set = so_set.sort do |a, b| a.weight.to_f <=> b.weight.to_f end
	so_set.reverse!
	food_list = [] + bs_set + so_set + as_set

	update = '*'

#### 食品の重量の変更
when 'weight'
	puts "Change weight<br>" if @debug
	order_no = order.to_i
	unit_value = BigDecimal( 0 )
	food_list[order_no].unit = unit
	food_list[order_no].init = food_init_
	food_rr_ = 1.0 if /[^0-9.]/ =~ food_rr_
	food_list[order_no].rr = food_rr_
	food_weight, unit_value = food_weight_check( unitv )
	food_list[order_no].unitv = food_weight

	# 食品ごとの単位読み込み
	uk = BigDecimal( '1' )
	if unit != 'g'
		r = db.query( "SELECT unit from #{$MYSQL_TB_EXT} WHERE FN='#{food_list[order_no].fn}';", false )
		unith = JSON.parse( r.first['unit'] )
		uk = unith[unit]
	end

	# 換算重量の小数点処理
	food_list[order_no].weight = unit_value * uk
	if food_list[order_no].weight >= 10
		food_list[order_no].weight = food_list[order_no].weight.round( 0 ).to_i
	elsif food_list[order_no].weight >= 1
		food_list[order_no].weight = food_list[order_no].weight.round( 1 ).to_f
	else
		food_list[order_no].weight = food_list[order_no].weight.round( 2 ).to_f
	end

	# 調理後重量の小数点処理
	food_list[order_no].ew = BigDecimal( food_list[order_no].weight.to_s ) * BigDecimal( food_list[order_no].rr.to_s )
	if food_list[order_no].ew >= 10
		food_list[order_no].ew = food_list[order_no].ew.round( 0 ).to_i
	elsif food_list[order_no].ew >= 1
		food_list[order_no].ew = food_list[order_no].ew.round( 1 ).to_f
	else
		food_list[order_no].ew = food_list[order_no].ew.round( 2 ).to_f
	end
	update = '*'


#### 食品番号による食品の追加、または空白の追加
when 'add'
	puts "Adding food / space<br>" if @debug
	fn = '' if fn == nil
	fn.gsub!( /　+/, ' ' )
	fn.gsub!( /\s+/, ' ' )
	fn.tr!( "０-９", "0-9" ) if /[０-９]/ =~ fn
	fn.sub!( '．', '.')
	p fn if @debug

	t = fn.split( ' ' )
	add_food_no = t[0]
	add_food_weight = 100
	add_food_weight = t[1] unless t[1] == nil
	add_food_weight = 100 unless /[0-9\.]+/ =~ t[1]
	add_food_no = '00000' if add_food_no == '0'
	p add_food_no if @debug

	insert_posi = 0
	check_flag = false
	food_list.size.times do |c|
		if food_list[c].check == "1"
			insert_posi = c
			check_flag = true
		end
	end
	insert_posi = food_list.size - 1 unless check_flag
	food_list_ = []
	0.upto( insert_posi ) do |c| food_list_ << food_list[c] end

	o = Sum.new( user )
	if add_food_no == nil
		o.fn = '-'
	elsif /\d{5}/ =~ add_food_no
		r = db.query( "SELECT FN from #{$MYSQL_TB_TAG} WHERE FN='#{add_food_no}';", false )
		o.load_sum( "#{add_food_no}:#{add_food_weight}:0:#{add_food_weight}:0::1.0:#{add_food_weight}" ) if r.first
	elsif /[PU]?\d{5}/ =~ add_food_no
		r = db.query( "SELECT FN from #{$MYSQL_TB_TAG} WHERE FN='#{add_food_no}' AND (( user='#{user.name}' AND public!='#{2}' ) OR public='1' );", false )
		o.load_sum( "#{add_food_no}:#{add_food_weight}:0:#{add_food_weight}:0::1.0:#{add_food_weight}" ) if r.first
	else
		o.load_sum( "+::::0:#{add_food_no}" )
	end
	food_list_ << o

	if check_flag
		insert_posi += 1
		insert_posi.upto( food_list.size - 1 ) do |c| food_list_ << food_list[c] end
	end
	food_list = food_list_

	update = '*'

when 'check_box'
	puts "Checkbox<br>" if @debug
	order_no = order.to_i
	check_status = food_check
	food_list[order_no].check = check_status


#### Switching all check box
when 'allSwitch'
	allSwitch = @cgi['allSwitch']
	puts "allSwitch:#{allSwitch}<br>" if @debug

	food_list.size.times do |c| food_list[c].check = allSwitch end
	all_check = 'CHECKED' if allSwitch == '1'

when 'dish'
	puts "Change dish num<br>" if @debug
	dish_num = 1 if dish_num == nil || dish_num == ''
	dish_num = 1 unless dish_num =~ /\d+/
	dish_num.tr!( "０-９", "0-9" ) if /[０-９]/ =~ dish_num.to_s
	update = '*'


when 'quick_save'
	puts "quick_save<br>" if @debug
	recipe = Recipe.new( user )
	recipe.load_db( code, true )
	recipe.sum = sum
	recipe.dish = dish_num
	recipe.update_db()

	food_no, food_weight, total_weight = extract_sum( recipe.sum, recipe.dish, 0 )
	fct = FCT.new( user, @fct_item, @fct_name, @fct_unit, @fct_frct, 1, 1 )
	fct.load_palette( @palette_bit_all )
	fct.set_food( food_no, food_weight, false )
	fct.calc
	fct.digit
	fct.save_fcz( recipe.name, 'recipe', recipe.code )

when 'gn_exchange'
	puts "gn_exchange<br>" if @debug
	c = 0
	food_list.each do |e|
		unless e.fn == '-' || e.fn == '+'
			weight_gn = proc_wf( BigDecimal( e.weight ) / dish_num )
			food_list[c].weight = weight_gn
			food_list[c].unit = '0'
			food_list[c].unitv = weight_gn
			food_list[c].ew = weight_gn * BigDecimal( e.rr )
		end
		c += 1
	end
	dish_num = 1
	update = '*'

#### 調味％
when 'chomis'
	total_weight = BigDecimal( 0 )
	target_weight = BigDecimal( 0 )
	food_list.each do |e|
		unless e.fn == '-' || e.fn == '+'
			if e.check == '1'
				target_weight += BigDecimal( e.weight )
			end
			total_weight += BigDecimal( e.weight )
		end
	end
	target_weight = total_weight if target_weight == 0
	chomi_rate = target_weight / 100
	chomi_rate = 1.0 if chomi_rate == 0


	r = db.query( "SELECT sum from #{$MYSQL_TB_RECIPE} WHERE code='#{chomi_code}';", false )
	if r.first
		 r.first['sum'].split( "\t" ).each do |e|
			t = Sum.new( user )
			t.load_sum( e )
			t.weight = ( BigDecimal( t.weight ) * chomi_rate ).round( 1 )
			t.unitv = t.weight
			t.ew = ( t.weight * BigDecimal( t.rr )).round( 1 )
			food_list << t
		end
	end
	update = '*'

#### Adjusting total food weight
when 'wadj'
	weight_adj = @cgi['weight_adj'].to_i
	puts "weight_adj:#{weight_adj}<br>" if @debug
	weight_ctrl, weight_checked, check_all = weight_calc( food_list, dish_num, adjew )
	wadj_rate = BigDecimal( weight_adj - ( weight_ctrl - weight_checked )) / ( weight_checked )
	food_list.size.times do |c|
		if ( food_list[c].check == '1' || check_all ) && food_list[c].weight != '-' && food_list[c].weight != '+'
			food_list[c].weight = proc_wf( BigDecimal( food_list[c].weight ) * wadj_rate )
			uv = food_weight_check( food_list[c].unitv ).last
			food_list[c].unitv = proc_wf( BigDecimal( uv ) * wadj_rate )
			food_list[c].ew = proc_wf( BigDecimal( food_list[c].ew ) * wadj_rate )
		end
	end
	update = '*'

when 'eadj'
	puts "Adjusting tootal food energy<br>" if @debug
	energy_adj = @cgi['energy_adj'].to_i
	puts "energy_adj:#{energy_adj}<br>" if @debug
	energy_ctrl, energy_checked, check_all = energy_calc( food_list, dish_num, adjew, db )
	eadj_rate = BigDecimal( energy_adj - ( energy_ctrl - energy_checked )) / ( energy_checked )
	food_list.size.times do |c|
		if food_list[c].check == '1' || check_all && food_list[c].weight != '-' && food_list[c].weight != '+'
			food_list[c].weight = proc_wf( BigDecimal( food_list[c].weight ) * eadj_rate )
			uv = food_weight_check( food_list[c].unitv ).last
			food_list[c].unitv = proc_wf( BigDecimal( uv ) * eadj_rate )
			food_list[c].ew = proc_wf( BigDecimal( food_list[c].ew ) * eadj_rate )
		end
	end
	update = '*'

when 'sadj'
	puts "Adjusting tootal food salt<br>" if @debug
	salt_adj = @cgi['salt_adj'].to_f
	puts "salt_adj:#{salt_adj}<br>" if @debug
	salt_ctrl, salt_checked, check_all = salt_calc( food_list, dish_num, adjew, db )
	sadj_rate = BigDecimal( salt_adj - ( salt_ctrl - salt_checked )) / ( salt_checked )
	food_list.size.times do |c|
		if food_list[c].check == '1' || check_all && food_list[c].weight != '-' && food_list[c].weight != '+'
			food_list[c].weight = proc_wf( BigDecimal( food_list[c].weight ) * sadj_rate )
			uv = food_weight_check( food_list[c].unitv ).last
			food_list[c].unitv = proc_wf( BigDecimal( uv ) * sadj_rate )
			food_list[c].ew = proc_wf( BigDecimal( food_list[c].ew ) * sadj_rate )
		end
	end
	update = '*'

when 'ladj'
	puts "Adjusting feeding rate by food loss<br>" if @debug

	loss_adj = @cgi['loss_adj'].to_i
	puts "loss_adj:#{loss_adj}<br>" if @debug

	weight_ctrl, weight_checked = weight_calc( food_list, dish_num )
	ladj_rate = ( BigDecimal( weight_checked - loss_adj ) / ( weight_checked )).round( 2 ).to_f
	food_list.size.times do |c|
		if food_list[c].weight != '-' && food_list[c].weight != '+'
			if food_list[c].check == '1'
				food_list[c].rr = ladj_rate
				food_list[c].ew = BigDecimal( food_list[c].weight ) * ladj_rate
			else
				food_list[c].rr = "1.0"
				food_list[c].ew = food_list[c].weight
			end
		end
	end
	update = '*'
end

update = '' if recipe_name == ''
puts "update:#{update}<br><hr>" if @debug


puts "Getting food weight & food energy & food salt<br>" if @debug
weight_ctrl, weight_checked = weight_calc( food_list, dish_num, adjew )
energy_ctrl, energy_checked = energy_calc( food_list, dish_num, adjew, db )
salt_ctrl, salt_checked = salt_calc( food_list, dish_num, adjew, db )
weitht_adj = weight_ctrl if weitht_adj == 0
energy_adj = energy_ctrl if energy_adj == 0
salt_adj = salt_ctrl if salt_adj == 0


puts "Loading CB tag<br>" if @debug
food_tag = []
if false
	food_list.each do |e|
		r = db.query( "SELECT Tagnames from #{$MYSQL_TB_FCT} WHERE FN='#{e.fn}';", false )
		food_tag << r.first['Tagnames'] if r.first
		food_tag << '' if e.fn == '-' || e.fn == '+'
	end
else
	food_list.each do |e|
		q = "SELECT * from #{$MYSQL_TB_TAG} WHERE FN='#{e.fn}';"
		q = "SELECT * from #{$MYSQL_TB_TAG} WHERE FN='#{e.fn}' AND user='#{user.name}';" if /^U\d{5}/ =~ e.fn
		r = db.query( q, false )
		food_tag << bind_tags( r ) if r.first
		food_tag << '' if e.fn == '-' || e.fn == '+'
	end
end


puts 'chomi % HTML<br>' if @debug
chomi_html = chomi_cell( l, code, chomi_selected, chomi_code, chomi_pub, db )

puts 'HTML upper part<br>' if @debug
html = <<-"UPPER_MENU"
<div class='container-fluid'>
	<div class='row'>
		<div class='col'><h5>#{l['cboard']}: #{update}#{recipe_name}</h5></div>
	</div>

	<div class='row'>
		<div class='col-2'>
			<div class='input-group input-group-sm'>
	        	<button class='btn btn-outline-primary' type='button' onclick=\"dishCB( '#{code}' )\">#{l['dish']}</button>
  				<input type="number" min='1' class="form-control" id="dish_num" value="#{dish_num}" onchange=\"dishCB( '#{code}' )\">
			</div>
		</div>
		<div class='col-3'>
			<div class='input-group input-group-sm'>
	        	<button class='btn btn-outline-primary' type='button' onclick=\"recipeAdd( '#{code}' )\">#{l['fn']}</button>
  				<input type="text" class="form-control" maxlength='12' placeholder="00000 100" id="food_add">
			</div>
		</div>
		<div class='col-6' id='chomi_cell'>
			#{chomi_html}
		</div>
		<div class='col-1'>
			<div class="form-check">
				<input class="form-check-input" type="checkbox" id="chomi_pub_check" onchange=\"selectChomiPub()\" #{$CHECK[chomi_pub == 1]}>
				<label class="form-check-label">#{l[:chomi_pub]}</label>
			</div>
		</div>
	</div>
	<br>

	<div class='row'>
		<div class='col-2'>
			<div class='input-group input-group-sm'>
	        	<button class='btn btn-outline-primary' type='button' onclick=\"weightAdj( '#{code}' )\">#{l['guide_g']}</button>
  				<input type="number" min='1' class="form-control" id="weight_adj" value="#{weight_ctrl.round}">
			</div>
		</div>

		<div class='col-2'>
			<div class='input-group input-group-sm'>
	        	<button class='btn btn-outline-primary' type='button' onclick=\"energyAdj( '#{code}' )\">#{l['guide_e']}</button>
 				<input type="number" min='1' class="form-control" id="energy_adj" value="#{energy_ctrl.round}">
			</div>
		</div>

		<div class='col-2'>
			<div class='input-group input-group-sm'>
	        	<button class='btn btn-outline-primary' type='button' onclick=\"saltAdj( '#{code}' )\">#{l['guide_s']}</button>
  				<input type="number" min='1' step="0.1" class="form-control" id="salt_adj" value="#{salt_ctrl.round( 1 ).to_f}">
			</div>
		</div>
		<div class='col-1'>
			<div class="form-check form-switch">
			  <input class="form-check-input" type="checkbox" id='adjew' onchange="changeAdjew( '#{code}' )" #{adjew_checked[adjew]}>
			  <label class="form-check-label">#{l['expect_g']}</label>
			</div>
		</div>
		<div class='col-2'>
			<div class='input-group input-group-sm'>
	        	<button class='btn btn-outline-primary' type='button' onclick=\"lossAdj( '#{code}' )\">#{l['waste']}</button>
  				<input type="number" min='0' class="form-control" id="loss_adj" value="0">
			</div>
		</div>
		<div class='col' align='right'>
			<input type='checkbox' id='gn_check'>&nbsp;
			<span class='badge rounded-pill npill' onclick=\"gnExchange( '#{code}' )\">#{l['gram']}</span>
			&nbsp;&nbsp;&nbsp;&nbsp;
			<input type='checkbox' id='all_check'>&nbsp;
			<span class='badge rounded-pill npill' onclick=\"clearCB( 'all', '#{code}' )\">#{l['reset']}</span>
		</div>
	</div>
	<hr>
UPPER_MENU

puts html

html = <<-"ITEM_NAME"
<div class='row cb_header'>
	<div class='col-2'>#{l['operation']}&nbsp;&nbsp;&nbsp;<input type='checkbox' id='switch_all' #{all_check} onclick=\"allSwitch( '#{code}' )\">&nbsp;#{l['fn']}</div>
	<div class='col-3'>#{l['food_name']}</div>
	<div class='col-3'>
  		<div class='row'>
			<div class='col-6'>#{l['memo']}</div>
			<div class='col-3'>#{l['simple_g']}&nbsp;<span onclick=\"sortCB( '#{code}' )\">#{l['sort']}</span></div>
			<div class='col-3'>#{l['expect_g']}</div>
		</div>
	</div>
	<div class='col-4'>
  		<div class='row'>
			<div class='col-3'>#{l['volume']}</div>
			<div class='col-4'>#{l['unit']}</div>
			<div class='col-3'>#{l['rrate']}</div>
		</div>
	</div>
</div>
<br>
ITEM_NAME
puts html

puts 'HTML food list part<br>' if @debug
c = 0
food_list.each do |e|
#	puts e.unit if user.status >= 8 && e.unit != 'g'

	# フードチェック
	check = ''
	check = 'CHECKED' if e.check == '1'

	# 単位の生成と選択
	unit_set = []
	unit_select = []
  	unless e.fn == '-' || e.fn == '+'
		r = db.query( "SELECT unit FROM #{$MYSQL_TB_EXT} WHERE FN='#{e.fn}';", false )
		if r.first
			unith = JSON.parse( r.first['unit'] )
			unith.each do |k, v|
				unless k == 'note'
					unit_set << k
					if k == e.unit
						unit_select << 'SELECTED'
					else
						unit_select << ''
					end
				end
			end
		end
	end

	puts 'Generating food key<br>' if @debug
	food_key = ''
  	unless e.fn == '-' || e.fn == '+'
  		q = "SELECT * FROM #{$MYSQL_TB_TAG} WHERE FN='#{e.fn}';"
		q = "SELECT * from #{$MYSQL_TB_TAG} WHERE FN='#{e.fn}' AND user='#{user.name}';" if /^U\d{5}/ =~ e.fn
		r = db.query( q, false )
		food_key = "#{r.first['FG']}:#{r.first['class1']}:#{r.first['class2']}:#{r.first['class3']}:#{r.first['name']}" if r.first
	end

	html = "<div class='row'>"
 	html << "	<div class='col-2'>"
 	html << "		<span onclick=\"upperCB( '#{c}', '#{code}' )\">#{l['up']}</span>"
 	html << "		<span onclick=\"lowerCB( '#{c}', '#{code}' )\">#{l['down']}</span>"
 	if e.fn == '-'
	  	html << "&nbsp;&nbsp;&nbsp;<input class='form-check-input' type='checkbox' id='food_cb#{c}' onchange=\"checkCB( '#{c}', '#{code}', 'food_cb#{c}' )\" #{check}></div>"
		html << "<div class='col-9'><hr></div>"
		html << "<div class='col-1'><span onclick=\"clearCB( '#{c}', '#{code}' )\">#{l['eraser']}</span></div>"
 	elsif e.fn == '+'
	  	html << "&nbsp;&nbsp;&nbsp;<input class='form-check-input' type='checkbox' id='food_cb#{c}' onchange=\"checkCB( '#{c}', '#{code}', 'food_cb#{c}' )\" #{check}></div>"
		html << "<div class='col-3 text-secondary cb_food_label' align='right'>( #{e.init} )</div>"
		html << "<div class='col-6'><hr></div>"
		html << "<div class='col-1'><span onclick=\"clearCB( '#{c}', '#{code}' )\">#{l['eraser']}</span></div>"
  	else

	  	html << "&nbsp;&nbsp;&nbsp;<input class='form-check-input' type='checkbox' id='food_cb#{c}' onchange=\"checkCB( '#{c}', '#{code}', 'food_cb#{c}' )\" #{check}>&nbsp;#{e.fn}</div>"
  		html << "	<div class='col-3 fct_value' onclick=\"cb_detail_sub( '#{food_key}', '#{e.weight}', '#{e.fn}' )\">#{food_tag[c]}</div>"
  		html << "	<div class='col-3'>"
  		html << "		<div class='row cb_form'>"
  		html << "			<div class='col-6'><input type='text'  maxlength='20' class='form-control form-control-sm' id='food_init_#{c}' value='#{e.init}' onchange=\"initCB_SS( '#{c}', 'unitv_#{c}', 'unit_#{c}', 'food_init_#{c}', 'food_rr_#{c}', '#{code}' )\"></div>"
  		html << "			<div align='right' class='col-3 fct_value'>#{e.weight.to_f}</div>"
  		html << "			<div align='right' class='col-3 fct_value'>#{e.ew.to_f}</div>"
		html << "		</div>"
		html << "	</div>"
  		html << "	<div class='col-4'>"
  		html << "		<div class='row cb_form'>"
  		if /\// =~ e.unitv.to_s
  			html << "			<div class='col-3'><input type='text' maxlength='5' class='form-control form-control-sm' id='unitv_#{c}' value='#{e.unitv}' onchange=\"weightCB( '#{c}', 'unitv_#{c}', 'unit_#{c}', 'food_init_#{c}', 'food_rr_#{c}', '#{code}' )\"></div>"
  		else
  			html << "			<div class='col-3'><input type='text' maxlength='5' class='form-control form-control-sm' id='unitv_#{c}' value='#{e.unitv.to_f}' onchange=\"weightCB( '#{c}', 'unitv_#{c}', 'unit_#{c}', 'food_init_#{c}', 'food_rr_#{c}', '#{code}' )\"></div>"
  		end
  		html << "			<div class='col-4'><select class='form-select form-select-sm' id='unit_#{c}' onchange=\"weightCB( '#{c}', 'unitv_#{c}', 'unit_#{c}', 'food_init_#{c}', 'food_rr_#{c}', '#{code}' )\">"
  		unit_set.size.times do |cc|
  			html << "				<option value='#{unit_set[cc]}' #{unit_select[cc]}>#{unit_set[cc]}</option>"
  		end
		html << "				</select>"
		html << "			</div>"
  		html << "			<div class='col-2'><input type='text' maxlength='3' class='form-control form-control-sm' id='food_rr_#{c}' value='#{e.rr}' onchange=\"weightCB( '#{c}', 'unitv_#{c}', 'unit_#{c}', 'food_init_#{c}', 'food_rr_#{c}', '#{code}' )\"></div>"
  		html << "			<div class='col-1'><span onclick=\"clearCB( '#{c}', '#{code}' )\">#{l['eraser']}</span></div>"
		html << "		</div>"
		html << "	</div>"
	end
	html << "</div>"

	puts html
	c += 1
end


puts 'HTML lower menu part<br>' if @debug
price_html = ''
if recipe_name != '' && update == ''
	price_html = "<div class='col-1 btn btn-light btn-sm nav_button' onclick=\"priceView( '#{code}' )\">#{l['price']}</div>" if recipe_name != '' && update == ''
else
	price_html = "<div class='col-1 btn btn-secondary btn-sm nav_button'>#{l['price']}</div>"
end

#### Quick Save
qsave_html =''
if recipe_name == '' || protect == 1 || user.name != recipe_user
	qsave_html = "<div class='col-1'></div>"
else
	qsave_html = "<div class='col-1'><span onclick=\"quickSave( '#{code}' )\">#{l['save']}</span></div>"
end

#### Quick Print
qprint_html = ''
if recipe_name == '' || user.name != recipe_user
	qprint_html = "<div class='col-1'></div>"
else
	qprint_html = "<div class='col-1'><span onclick=\"print_templateSelect( '#{code}' )\">#{l['printer']}</span></div>"
end


foot_html = <<-"LOWER_MENU"
<br>
	<div class='row'>
		<div class='col-1 btn btn-light btn-sm nav_button' onclick="recipeEdit( 'init', '#{code}' )" align='justify'>#{l['recipe']}</div>
		<div class='col-1 btn btn-light btn-sm nav_button' onclick="calcView( '#{code}' )">#{l['calc']}</div>
		#{price_html}
		<div class='col-1 btn btn-light btn-sm nav_button' onclick="luckyInput()">#{l['lucky']}</div>
		<div class='col-1 btn btn-light btn-sm nav_button' onclick='Pseudo_R2F("#{code}")'>#{l['foodize']}</div>
		<div class='col-1 btn btn-light btn-sm nav_button' onclick='initDetective()'>#{l['detective']}</div>
		<div class='col-4'></div>
		#{qsave_html}
		#{qprint_html}
	</div>
	<div class='code'>#{code}</div>
</div>
LOWER_MENU

puts foot_html


#==============================================================================
# POST PROCESS
#==============================================================================

puts 'Updating cboard sum<br>' if @debug
sum_new = ''
food_list.each do |e| sum_new << "#{e.fn}:#{e.weight}:#{e.unit}:#{e.unitv}:#{e.check}:#{e.init}:#{e.rr}:#{e.ew}\t" end
sum_new.chop!
db.query( "UPDATE #{$MYSQL_TB_SUM} set code='#{code}', name='#{recipe_name}', sum='#{sum_new}', dish='#{dish_num}', protect='#{protect}' WHERE user='#{user.name}';", true ) unless user.status == 7

puts 'Updating config<br>' if @debug
cfg.val['chomi_pub'] = chomi_pub
cfg.update()

puts 'Updating history<br>' if @debug
add_his( user, code ) if command == 'load'

#==============================================================================
# FRONT SCRIPT START
#==============================================================================
if command == 'init' || command == 'load'
	js = <<-"JS"
<script type='text/javascript'>

var postReqCB = ( command, data, successCallback ) => {
	$.post( '#{myself}', { command, ...data })
		.done( successCallback )
		.fail(( jqXHR, textStatus, errorThrown ) => {
			console.error( "Request failed: ", textStatus, errorThrown );
			alert( "An error occurred. Please try again." );
		});
};

// Clear foods, and reload CB counter
var clearCB = ( order, code ) => {
    if ( order === 'all' && $( '#all_check' ).is( ':checked' )) {
        postReqCB( 'clear', { food_check: 'all', code }, data => $( "#L1" ).html( data ));

        flashBW();
        dl1 = true;
        displayBW();

    } else if ( order !== 'all' ) {
        postReqCB( 'clear', { order, code }, data => $( "#L1" ).html( data ));

    } else {
        displayVIDEO( '(>_<)check!' );

    }
    setTimeout( refreshCBN, 1000 );
    checkCalc( code );
};

var upperCB = ( order, code ) => postReqCB( 'upper', { order, code }, data => $( "#L1" ).html( data ));
var lowerCB = ( order, code ) => postReqCB( 'lower', { order, code }, data => $( "#L1" ).html( data ));

var dishCB = ( code ) => {
	const dish_num = $( '#dish_num' ).val();
	postReqCB( 'dish', { code, dish_num }, data => {
		$( "#L1" ).html( data );
    	checkCalc( code );
	});
};

// Adjust total food weight
var weightAdj = ( code ) => {
	const weight_adj = $( '#weight_adj' ).val();
	postReqCB( 'wadj', { code, weight_adj }, data => {
		$( "#L1" ).html( data );
		checkCalc( code );
	});
};

// Adjust total food energy
var energyAdj = ( code ) => {
	const energy_adj = $( '#energy_adj' ).val();
	postReqCB( 'eadj', { code, energy_adj }, data => {
		$( "#L1" ).html( data );
    	checkCalc( code );
	});
};

// Adjust total food salt
var saltAdj = ( code ) => {
	const salt_adj = $( '#salt_adj' ).val();
	postReqCB( 'sadj', { code, salt_adj }, data => {
		$( "#L1" ).html( data );
    	checkCalc( code );
	});
};

// Switch Adjust weight mode
var changeAdjew = ( code ) => {
	const adjew = $( '#adjew' ).is( ':checked' ) ? 1 : 0;
	postReqCB( 'adjew', { adjew }, data => {
		$( "#L1" ).html( data );
    	checkCalc( code );
	});
};

// Adjust feeding rate by food loss
var lossAdj = ( code ) => {
	const loss_adj = $( '#loss_adj' ).val();
	postReqCB( 'ladj', { code, loss_adj }, data => {
		$( "#L1" ).html( data );
    	checkCalc( code );
	});
};

// Sort sum list by food weight
var sortCB = ( code ) => postReqCB( 'sort', { code }, data => $( "#L1" ).html( data ));

// Add a food or a delimiter
var recipeAdd = ( code ) => {
	const fn = $( '#food_add' ).val();
	postReqCB( 'add', { fn, code }, data => $( "#L1" ).html( data ));
	setTimeout( refreshCBN, 1000 );
};

// Update sum
var weightCB = ( order, unitv_id, unit_id, food_init_id, food_rr_id, code ) => {
	const unitv = $( '#' + unitv_id ).val();
	const unit = $( '#' + unit_id ).val();
	const food_init = $( '#' + food_init_id ).val();
	const food_rr = $( '#' + food_rr_id ).val();
	postReqCB( 'weight', { order, unitv, unit, code, food_init, food_rr }, data => {
		$( "#L1" ).html( data );
		checkCalc( code );
	});
};

// Update sum by hidden
var initCB_SS = ( order, unitv_id, unit_id, food_init_id, food_rr_id, code ) => {
	const unitv = $( '#' + unitv_id ).val();
	const unit = $( '#' + unit_id ).val();
	const food_init = $( '#' + food_init_id ).val();
	const food_rr = $( '#' + food_rr_id ).val();
	postReqCB( 'weight', { order, unitv, unit, code, food_init, food_rr });
};

// Foods check process
var checkCB = ( order, code, check_id ) => {
	const checked = $( '#' + 'check_id' ).is( ':checked' ) ? 1 : 0;
	postReqCB( 'check_box', { order, food_check: checked, code });
};

// Switching all check box
var allSwitch = ( code ) => {
	const allSwitch = $( '#switch_all' ).is( ':checked' ) ? 1 : 0;
	postReqCB( 'allSwitch', { code, allSwitch }, data => $( "#L1" ).html( data ));
};

// Quick Save
var quickSave = ( code ) => postReqCB( 'quick_save', { code }, data => {
	$( "#L1" ).html( data );
	displayREC();
});

// GN Exchange
var gnExchange = ( code ) => {
	if ( $( '#gn_check' ).is( ':checked' )) {
		postReqCB('gn_exchange', { code }, data => {
			$( "#L1" ).html( data );
    		checkCalc( code );
		});
	} else {
		displayVIDEO('Check!!(>_<)');
	}
};

// Chomi% category
var chomiSelect = () => {
	const code = $( '#recipe_code' ).val();
	const chomi_selected = $( '#chomi_selected' ).val();
	postReqCB( 'chomi_cell', { code, chomi_selected }, data => $( "#chomi_cell" ).html( data ));
};

// Chomi% add
var chomiAdd = ( source_code ) => {
	const code = $( '#recipe_code' ).val();
	const chomi_selected = $( '#chomi_selected' ).val();
	const chomi_code = $( '#chomi_code' ).val();
	postReqCB( 'chomis', { code, chomi_selected, chomi_code }, data => {
		$( "#L1" ).html( data );
    	checkCalc( source_code );
	});
};

// Chomi% public
var selectChomiPub = () => {
	const chomi_pub = $( '#chomi_pub_check' ).is( ':checked' ) ? 1 : 0;
	postReqCB( 'reload', { chomi_pub }, data => $( "#L1" ).html( data ));
};

// Retrun to CB
var returnCB = () => {
	flashBW();
	dl1 = true;
	displayBW();
};

// Retrun to CB
var checkCalc = ( code ) => {
	if ( $( "#calc" ).length ){ recalcView( code );}
};

</script>

JS

	puts js
end
