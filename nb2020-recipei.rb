#! /usr/bin/ruby
#encoding: utf-8
#Nutrition browser 2020 recipe search index & fcz builder & 0.2.0 (2024/07/14)


#==============================================================================
#LIBRARY
#==============================================================================
require './nb2020-soul'
require './nb2020-brain'
require 'natto'


#==============================================================================
#STATIC
#==============================================================================
@debug = false
#$UDIC = '/usr/local/share/mecab/dic/ipadic/sys.dic'


#==============================================================================
#DEFINITION
#==============================================================================


#==============================================================================
# Main
#==============================================================================

mecab = Natto::MeCab.new()
db = Mysql2::Client.new(:host => "#{$MYSQL_HOST}", :username => "#{$MYSQL_USER}", :password => "#{$MYSQL_PW}", :database => "#{$MYSQL_DB}", :encoding => "utf8" )


#### Makeing alias dictionary
puts "Makeing alias dictionary."
dic = Hash.new
res = db.query( "SELECT org_name, alias FROM #{$MYSQL_TB_DIC};" )
res.each do |e| dic[e['alias']] = e['org_name'] end


#### Lording all recipe list
puts "Analyzing recipe data.\n"
res = db.query( "SELECT code, name, sum, protocol, public, user FROM #{$MYSQL_TB_RECIPE};" )
res.each do |e|
	print "#{e['code']}\r"
	target = []

	#recipe name
	target << e['name']
	res2 = db.query( "SELECT * FROM #{$MYSQL_TB_RECIPEI} WHERE code='#{e['code']}' AND word='#{e['name']}' AND user='#{e['user']}';" )
	db.query( "INSERT INTO #{$MYSQL_TB_RECIPEI}  SET public='#{e['public']}', user='#{e['user']}', code='#{e['code']}', word='#{e['name']}';" ) unless res2.first

	a = e['protocol'].split( "\n" )
	#tag line
	if a[0] != nil && /^\#.+/ =~ a[0]
		a[0].gsub!( '#', '' )
		if a[0] != ''
			a[0].gsub!( "　", "\s" )
			a[0].gsub!( '・', "\t" )
			a[0].gsub!( '／', "\t" )
			a[0].gsub!( '(', "\t" )
			a[0].gsub!( ')', "\t" )
			a[0].gsub!( '（', "\t" )
			a[0].gsub!( '）', "\t" )
			a[0].gsub!( /\t+/, "\s" )
			tags = a[0].split( "\s" )
			tags.each do |ee|
				if ee != ''
					target << ee
					res2 = db.query( "SELECT * FROM #{$MYSQL_TB_RECIPEI} WHERE code='#{e['code']}' AND word='#{ee}' AND user='#{e['user']}';" )
					db.query( "INSERT INTO #{$MYSQL_TB_RECIPEI}  SET public='#{e['public']}', user='#{e['user']}', code='#{e['code']}', word='#{ee}';" ) unless res2.first
				end
			end
		end
	end

	#comment line
	if a[1] != nil && /^\#.+/ =~ a[1]
		a[1].gsub!( '#', '' )
		target << a[1] if a[1] != ''
	end

	target.each do |ee|
		true_word = ee
		true_word = dic[ee] if dic[ee] != nil
		mecab.parse( true_word ) do |n|
			a = n.feature.force_encoding( 'utf-8' ).split( ',' )
		 	if a[0] == '名詞' && ( a[1] == '一般' || a[1] == '固有名詞' || a[1] == '普通名詞'  || a[1] == '人名' )
				res2 = db.query( "SELECT * FROM #{$MYSQL_TB_RECIPEI} WHERE code='#{e['code']}' AND user='#{e['user']}' AND code='#{e['code']}' AND word='#{n.surface}';" )
				db.query( "INSERT INTO #{$MYSQL_TB_RECIPEI}  SET public='#{e['public']}', user='#{e['user']}', code='#{e['code']}', word='#{n.surface}';" ) unless res2.first
		 	end
		end
	end

	#foods
	a = e['sum'].split( "\t" )
	sum_code = []
	target_food = []
	a.each do |ee| sum_code << ee.split( ':' ).first end
	sum_code.each do |ee|
		res2 = db.query( "SELECT name FROM #{$MYSQL_TB_TAG} WHERE FN='#{ee}';" )
		target_food << res2.first['name'] if res2.first
	end

	target_food.each do |ee|
		res2 = db.query( "SELECT * FROM #{$MYSQL_TB_RECIPEI} WHERE user='#{e['user']}' AND code='#{e['code']}' AND word='#{ee}';" )
		db.query( "INSERT INTO #{$MYSQL_TB_RECIPEI}  SET public='#{e['public']}', user='#{e['user']}', code='#{e['code']}', word='#{ee}';" ) unless res2.first
	end
end


#### Deleting non-existent recipe index
puts "\nDeleting non-existent recipe index."
db.query( "DELETE #{$MYSQL_TB_RECIPEI} FROM #{$MYSQL_TB_RECIPEI} LEFT OUTER JOIN #{$MYSQL_TB_RECIPE} ON #{$MYSQL_TB_RECIPE}.code=#{$MYSQL_TB_RECIPEI}.code WHERE #{$MYSQL_TB_RECIPE}.code IS NULL;" )
puts "Done.\n"

#### ========================================================================
puts "Calculating recipe FCZ.\n"
user = User.new()

res = db.query( "SELECT * FROM #{$MYSQL_TB_RECIPE};" )
res.each do |e|
	user.name = e['user']
	unless e['dish'].to_i == 0
		food_no, food_weight, total_weight = extract_sum( e['sum'], e['dish'], 0 )
		fct = FCT.new( user, @fct_item, @fct_name, @fct_unit, @fct_frct, 1, 1 )
		fct.load_palette( @palette_bit_all )
		fct.set_food( food_no, food_weight, false )
		fct.calc
		fct.digit

		fct.save_fcz( e['name'], 'recipe', e['code'] )
	end
end


#### Deleting non-existent recipe FCZ
puts "\nDeleting non-existent recipe FCZ."
db.query( "DELETE #{$MYSQL_TB_FCZ} FROM #{$MYSQL_TB_FCZ} LEFT OUTER JOIN #{$MYSQL_TB_RECIPE} ON #{$MYSQL_TB_RECIPE}.code=#{$MYSQL_TB_FCZ}.origin WHERE #{$MYSQL_TB_RECIPE}.code IS NULL AND #{$MYSQL_TB_FCZ}.base='recipe';" )
puts "Done."
