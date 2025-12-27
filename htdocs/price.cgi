#! /usr/bin/ruby
#encoding: utf-8
#Nutrition browser 2020 price editor 0.1.0 (2025/12/21)

#==============================================================================
#STATIC
#==============================================================================
@debug = false
myself = File.basename( __FILE__ )

#==============================================================================
#LIBRARY
#==============================================================================
require './soul'

#==============================================================================
#DEFINITION
#==============================================================================
# Language pack
def language_pack( language )
	l = Hash.new

	#Japanese
	l['ja'] = {
		price:	"原価計算:",
		apllay:	 "目安費用反映",
		apllaym:	"マスター価格適用",
		registm:	"マスター価格登録",
		reset:	"計算表 初期化",
		food_name:	"食品名",
		volume:	"購入量（g）",
		pyament:	"支払金額（円）",
		use_g:	"使用量（g）",
		genka:	"原価（円）",
		genka_total:	"原価合計"
	}

	return l[language]
end

#==============================================================================
# Main
#==============================================================================
html_init( nil )

user = User.new( @cgi )
l = language_pack( user.language )
db = Db.new( user, @debug, false )


#### POSTデータの取得
command = @cgi['command']
code = @cgi['code']
food_volume_p = @cgi['food_volume'].to_i
food_price_p = @cgi['food_price'].to_i
food_no_p = @cgi['food_no']
if @debug
	puts "command:#{command}<br>"
	puts "code:#{code}<br>"
	puts "food_volume:#{food_volume_p}<br>"
	puts "food_price:#{food_price_p}<br>"
	puts "food_no:#{food_no_p}<br>"
	puts "<hr>"
end


#### 基礎データの作成
solid = []
recipe_food_no = []
food_use = []

# レシピデータの読み込み
res = db.query( "SELECT name, sum, dish, protect from #{$TB_RECIPE} WHERE code=?", false, [code] )&.first
if res
	recipe_name = res['name']
	dish_num = res['dish'].to_i
	recipe_protect = res['protect'].to_i

	# 食品番号と１人分の使用量を抽出
	solid = res['sum'].split( "\t" )
	solid.each do |e|
		a = e.split( ':' )
		unless a[0] == '-' || a[0] == '+'
			recipe_food_no << a[0]
			food_use << ( BigDecimal( a[1] ) / dish_num )
		end
	end
end

#### 原価データの読み込み
food_no = []
food_price = []
food_volume = []

res = db.query( "SELECT * FROM #{$TB_PRICE} WHERE code=?", false, [code] )&.first
if res
	solid = res['price'].split( "\t" )
	solid.each do |e|
		a = e.split( ':' )
		if recipe_food_no.include?( a.first )
			food_no << a[0]
			food_volume << a[1].to_i
			food_price << a[2].to_i
		end
	end
# 新規原価表の作成
else
	new_price = ''
	recipe_food_no.each do |e|
		food_no << e
		food_volume << 0
		food_price << 0
		new_price << "#{e}::\t"
	end
	new_price.chop!
	db.query( "INSERT INTO #{$TB_PRICE} SET code=?, user=?, price=?", false, [code, user.name, new_price] )
end


#### 個別コマンド
html = ''
case command
# 購入量変更
when 'changeFV'
	food_no.size.times do |c|
		food_volume[c] = food_volume_p if food_no[c] == food_no_p
	end
# 支払金額変更
when 'changeFP'
	food_no.size.times do |c|
		food_price[c] = food_price_p if food_no[c] == food_no_p
	end
# 初期化
when 'clearCT'
	food_no.size.times do |c|
		food_volume[c] = 0
		food_price[c] = 0
	end
# マスター価格適応
when 'adpt_master'
	food_no.size.times do |c|
		res = db.query( "SELECT volume, price FROM #{$TB_PRICEM} WHERE FN=? AND user=?", false, [food_no[c], user.name] )&.first
		if res
			food_volume[c] = res['volume']
			food_price[c] = res['price']
		end
	end
# マスター価格登録
when 'reg_master'
	food_no.size.times do |c|
		if food_volume[c].to_i != 0 && food_price[c].to_i != 0
			res = db.query( "SELECT FN FROM #{$TB_PRICEM} WHERE FN=? AND user=?", false, [food_no[c], user.name] )&.first

			# マスター価格の登録、または更新
			if res
				db.query( "UPDATE TABLE #{$TB_PRICEM} SET volume=?, price=? WHERE FN=? AND user=?", false, [food_volume[c], food_price[c], food_no[c], user.name] )
			else
				db.query( "INSERT INTO #{$TB_PRICEM} SET volume=?, price=?, FN=?, user=?", false, [food_volume[c], food_price[c], food_no[c], user.name] )
			end
		else
			# 未設定のマスター価格の削除
			db.query( "DELETE FROM #{$TB_PRICEM} WHERE FN=? AND user=?", false, [food_no[c], user.name] )
		end
	end
end


#### 名前の書き換え
food_name = []
food_no.size.times do |c|
	res = db.query( "SELECT * from #{$TB_TAG} WHERE FN=?", false, [food_no[c]] )&.first
	food_name[c] = tagnames( res ) if res
end


#### 原価の計算
food_cost = []
total_cost = 0
food_no.each_index do |c|
	if food_volume[c].to_i > 0 && food_price[c].to_i > 0
		cost = ( BigDecimal( food_use[c] ) / food_volume[c] * food_price[c] ).ceil
		food_cost << cost
		total_cost += cost
	else
		food_cost << 0
	end
end


#### レシピ価格区分反映
if command == 'ref_recipe'
	cost = 0
	if total_cost > 0 and total_cost < 50
		cost = 1
	elsif total_cost >= 50 and total_cost < 100
		cost = 2
	elsif total_cost >= 100 and total_cost < 150
		cost = 3
	elsif total_cost >= 150 and total_cost < 200
		cost = 4
	elsif total_cost >= 200 and total_cost < 300
		cost = 5
	elsif total_cost >= 300 and total_cost < 400
		cost = 6
	elsif total_cost >= 400 and total_cost < 500
		cost = 7
	elsif total_cost >= 500 and total_cost < 600
		cost = 8
	elsif total_cost >= 600 and total_cost < 800
		cost = 9
	elsif total_cost >= 800 and total_cost < 1000
		cost = 10
	else
		cost = 11
	end

	db.query( "UPDATE #{$TB_RECIPE} SET cost=? WHERE user=? and code=?", false, [cost, user.name, code] )
end


#### 価格区分反映ボタン
ref_recipe_button = ''
if recipe_protect == 0
	ref_recipe_button = "<button type='button' class='btn btn-outline-primary btn-sm' onclick=\"recipeRef( '#{code}' )\">#{l[:apllay]}</button>"
end


html = <<-"HTML"
<div class='container-fluid'>
<div class='row'>
	<h5>#{l[:price]} #{recipe_name}</h5></div><br>
	<div class='row'>
		<div class='col-3'>
			<button type='button' class='btn btn-outline-primary btn-sm' onclick="pricemAdpt( '#{code}' )">#{l[:apllaym]}</button>
		</div>
		<div class='col-3'>
			<button type='button' class='btn btn-outline-primary btn-sm' onclick="pricemReg( '#{code}' )">#{l[:registm]}</button>
		</div>
		<div class='col-3'>
			#{ref_recipe_button}
		</div>
		<div class='col-3' align='center'>
			<input type='checkbox' id='clearCT_check'>&nbsp;
			<button type='button' class='btn btn-outline-danger btn-sm' onclick="clearCT( '#{code}' )">#{l[:reset]}</button>
		</div>
	</div>
</div>
<hr>
<div class='container'>
	<div class='row'>
		<div class='col-3 cb_header'>#{l[:food_name]}</div>
		<div class='col-2 cb_header'>#{l[:volume]}</div>
		<div class='col-2 cb_header'>#{l[:pyament]}</div>
		<div class='col-2 cb_header'>#{l[:use_g]}</div>
		<div class='col-2 cb_header'>#{l[:genka]}</div>
	</div>
</div>
<br>

HTML

html << "<div class='container'>"
food_no.size.times do |c|
	html << "<div class='row'>"
	html << "	<div class='col-3'>#{food_name[c]}</div>"
	html << "	<div class='col-2'><input type='number' class='form-control form-control-sm' id='food_volume#{c}' value='#{food_volume[c]}' onchange=\"changeFV( '#{code}', 'food_volume#{c}', '#{food_no[c]}' )\"></div>"
	html << "	<div class='col-2'><input type='number' class='form-control form-control-sm' id='food_price#{c}' value='#{food_price[c]}' onchange=\"changeFP( '#{code}', 'food_price#{c}', '#{food_no[c]}' )\"></div>"
	html << "	<div class='col-2'>#{food_use[c].to_f}</div>"
	html << "	<div class='col-2'>#{food_cost[c]}</div>"
	html << "</div>"
end
	html << "<hr>"
	html << "<div class='row'>"
	html << "	<div class='col-9'>#{l[:genka_total]}</div>"
	html << "	<div class='col-2'>#{total_cost}</div>"
	html << "</div>"
html << "</div>"

html << "<div align='right' class='code'>#{code}</div>"

puts html


#### 原価計算表更新
new_price = ''
food_no.size.times do |c| new_price << "#{food_no[c]}:#{food_volume[c]}:#{food_price[c]}\t" end
new_price.chop!

db.query( "UPDATE #{$TB_PRICE} SET price=? WHERE code=? AND user=?", false, [new_price, code, user.name] )
