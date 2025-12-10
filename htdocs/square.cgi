#! /usr/bin/ruby
#encoding: utf-8
#Nutrition browser 2020 food square 0.2.5 (2025/07/27)


#==============================================================================
# STATIC
#==============================================================================
@debug = false
myself = File.basename( __FILE__ )

#==============================================================================
# LIBRARY
#==============================================================================
require './soul'

#==============================================================================
# DEFINITION
#==============================================================================

# Language pack
def language_pack( language )
	l = Hash.new

	#Japanese
	l['jp'] = {
		:plus 		=> "<img src='bootstrap-dist/icons/plus-square-fill.svg' style='height:2em; width:2em;'>",\
		:signpost	=> "<img src='bootstrap-dist/icons/signpost.svg' style='height:2em; width:2em;'>"
	}

	return l[language]
end

#### 名前の履歴の取得
def get_history_name( fg, db )
	name_his = []
	if db.user.name
		r = db.query( "SELECT his FROM #{$MYSQL_TB_HIS} WHERE user='#{db.user.name}';", false )
		if r.first
			his_raw = r.first['his'].split( "\t" )
			his_raw.map! do |x|
				x = "'#{x}'" if x.size <= 6
			end
			his_raw.compact!
			his = his_raw.join( ',' )

			unless his == ''
				rr = db.query( "SELECT name FROM #{$MYSQL_TB_TAG} WHERE FG='#{fg}' AND FN IN (#{his});", false )
				rr.each do |e| name_his << e['name'] end
			end
		end
	end

	return name_his
end


# ダイレクトグループの作成
def make_direct_group( direct_group, name_his, fg, class1, class2, class3, direct, pseudo_bit )
	dg_html = ''
	direct_group.uniq.each do |e|
		if name_his.include?( e )
			@his_class = pseudo_bit == 1 ? 'btn btn-outline-success btn-sm nav_button visited' : 'btn btn-outline-primary btn-sm nav_button visited'
		else
			@his_class = pseudo_bit == 1 ? 'btn btn-outline-dark btn-sm nav_button' : 'btn btn-outline-secondary btn-sm nav_button'
		end
		dg_html << "<button type='button' class='#{@his_class}' onclick=\"viewDetailSub( 'init', '#{fg}:#{class1}:#{class2}:#{class3}:#{e}', #{direct} )\">#{e}</button>\n"
	end

	return dg_html
end


#==============================================================================
# Main
#==============================================================================
html_init( nil )

user = User.new( @cgi )
user.debug if @debug
l = language_pack( user.language )
db = Db.new( user, @debug, false )

#### GET data
get_data = get_data()
channel = get_data['channel']
category = get_data['category'].to_s
food_key = CGI.unescape( get_data['food_key'] ) if get_data['food_key'] != '' && get_data['food_key'] != nil
frct_mode = get_data['frct_mode'].to_i
food_weight = CGI.unescape( get_data['food_weight'] ) if get_data['food_weight'] != '' && get_data['food_weight'] != nil
food_no = get_data['food_no']
base = get_data['base']
base_fn = get_data['base_fn']
if @debug
	puts "channel: #{channel}<br>"
	puts "category: #{category}<br>"
	puts "food_key: #{food_key}<br>"
	puts "frct_mode: #{frct_mode}<br>"
	puts "food_weight: #{food_weight}<br>"
	puts "food_no: #{food_no}<br>"
	puts "base: #{base}<br>"
	puts "base_fn: #{base_fn}<br>"
	puts "<hr>"
end


#### 食品グループ番号の桁補完
fg_no = category.empty? ? food_key.split( ':' ).shift : @fg[category.to_i]
puts "fg_no: #{fg_no}<br>" if @debug


#### 名前の履歴の取得
name_his = get_history_name( fg_no, db )
#puts "name_his: #{name_his}<br>" if @debug


puts 'Key chain<br>' if @debug
food_key = '' if food_key == nil
fg_key, class1, class2, class3, food_name = food_key.split( ':' )

class_name = ''
class_no = 0
unless class1 == nil || class1 == ''
	class_name = class1
	class_no = 1
end
unless class2 == nil || class2 == ''
	class_name = class2
	class_no = 2
end
unless class3 == nil || class3 == ''
	class_name = class3
	class_no = 3
end
if @debug
	puts "fg_key: #{fg_key}<br>"
	puts "class1: #{class1}<br>"
	puts "class2: #{class2}<br>"
	puts "class3: #{class3}<br>"
	puts "class_no: #{class_no}<br>"
	puts "class_name: #{class_name}<br>"
	puts "<hr>"
end


#### 閲覧選択
html = ''
class_html =''
direct_html = ''
pseudo_button = ''
class1_group = []
class2_group = []
class3_group = []
direct_group = []
class1_group_p = []
class2_group_p = []
class3_group_p = []
direct_group_p = []

case channel
#### 第１層閲覧選択ページ
when 'fctb'

	# 正規食品
	r = db.query( "SELECT * FROM #{$MYSQL_TB_TAG} WHERE FG='#{fg_no}' AND status='9' GROUP BY SN;", false )
	r.each do |e|
		if e['class1'] != ''
			class1_group << e['class1']
		elsif e['class2'] != ''
			class2_group << e['class2']
		elsif e['class3'] != ''
			class3_group << e['class3']
		else
			direct_group << e['name']
		end
	end
	[ class1_group, class2_group, class3_group ].each( &:uniq! )

	# Classグループの作成
	tag_button = "<button type='button' class='btn btn-info btn-sm nav_button'"
	class1_group.each do |e| class_html << "#{tag_button} onclick=\"summonL2( '#{fg_no}:#{e}:::' )\">#{e.sub( '+', '' ).sub( /^.+\-/, '' )}</button>\n" end
	class2_group.each do |e| class_html << "#{tag_button} onclick=\"summonL2( '#{fg_no}::#{e}::' )\">#{e.sub( '+', '' ).sub( /^.+\-/, '' )}</button>\n" end
	class3_group.each do |e| class_html << "#{tag_button} onclick=\"summonL2( '#{fg_no}:::#{e}:' )\">#{e.sub( '+', '' ).sub( /^.+\-/, '' )}</button>\n" end

	# ダイレクトグループの作成
	direct_html = make_direct_group( direct_group, name_his, fg_no, '', '', '', 1, 0 )

	# 擬似食品
	unless user.status == 0
		r = db.query( "SELECT * FROM #{$MYSQL_TB_TAG} WHERE FG='#{fg_no}' AND (( user='#{user.name}' AND status='1' ) OR status='2' OR status='3' );", false )
		r.each do |e|
			if e['class1'].to_s != ''
				class1_group_p << e['class1']
			elsif e['class2'].to_s != ''
				class2_group_p << e['class2']
			elsif e['class3'].to_s != ''
				class3_group_p << e['class3']
			else
				direct_group_p << e['name']
			end
		end

		class1_group_p = class1_group_p.uniq - class1_group
		class2_group_p = class2_group_p.uniq - class2_group
		class3_group_p = class3_group_p.uniq - class3_group

		# Classグループの作成
		tag_button = "<button type='button' class='btn btn-secondary btn-sm nav_button'"
		class1_group_p.each do |e| class_html << "#{tag_button} onclick=\"summonL2( '#{fg_no}:#{e}:::' )\">#{e.sub( '+', '' ).sub( /^.+\-/, '' )}</button>\n" end
		class2_group_p.each do |e| class_html << "#{tag_button} onclick=\"summonL2( '#{fg_no}::#{e}::' )\">#{e.sub( '+', '' ).sub( /^.+\-/, '' )}</button>\n" end
		class3_group_p.each do |e| class_html << "#{tag_button} onclick=\"summonL2( '#{fg_no}:::#{e}:' )\">#{e.sub( '+', '' ).sub( /^.+\-/, '' )}</button>\n" end

		# ダイレクトグループの作成
		direct_html << make_direct_group( direct_group_p, name_his, fg_no, '', '', '', 1, 1 )
	end

	# 擬似食品ボタンの作成
	pseudo_button = "<span onclick=\"pseudoAdd( 'init', '#{fg_no}::::', '' )\">#{l[:plus]}</span>\n" if user.status > 0

	html = <<-"HTML"
	<h6>#{category}.#{@category[category.to_i]}</h6>
	#{class_html}
	#{direct_html}
	#{pseudo_button}
HTML


#### 第２層閲覧選択ページ
when 'fctb_l2'
	# 正規食品
	r = db.query( "SELECT * FROM #{$MYSQL_TB_TAG} WHERE FG='#{fg_key}' AND class#{class_no}='#{class_name}' AND status='9' GROUP BY SN;", false )
	r.each do |e|
		if e['class1'] != '' && e['class2'] != ''
			class2_group << e['class2']
		elsif e['class1'] == '' && e['class2'] != '' && e['class3'] != ''
			class3_group << e['class3']
		elsif e['class1'] != '' && e['class2'] == '' && e['class3'] != ''
			class3_group << e['class3']
		else
			direct_group << e['name']
		end
	end
	class2_group.uniq!
	class3_group.uniq!


	# Classグループの作成
	tag_button = "<button type='button' class='btn btn-info btn-sm nav_button'"
	class2_group.each do |e| class_html << "#{tag_button} onclick=\"summonL3( '#{fg_key}:#{class1}:#{e}:#{class3}:#{food_name}', 3 )\">#{e.sub( '+', '' ).sub( /^.+\-/, '' )}</button>\n" end
	class3_group.each do |e| class_html << "#{tag_button} onclick=\"summonL3( '#{fg_key}:#{class1}:#{class2}:#{e}:#{food_name}', 3 )\">#{e.sub( '+', '' ).sub( /^.+\-/, '' )}</button>\n" end

	# ダイレクトグループの作成
	direct_html = make_direct_group( direct_group, name_his, fg_key, class1, class2, class3, 2, 0 )


	# 擬似食品
	unless user.status == 0
		r = db.query( "SELECT * FROM #{$MYSQL_TB_TAG} WHERE FG= '#{fg_key}' AND class#{class_no}='#{class_name}' AND (( user='#{user.name}' AND status='1' ) OR status='2' OR status='3' );", false )
		r.each do |e|
			if e['class1'].to_s != '' && e['class2'].to_s != ''
				class2_group_p << e['class2']
			elsif e['class1'].to_s == '' && e['class2'].to_s != '' && e['class3'].to_s != ''
				class3_group_p << e['class3']
			elsif e['class1'].to_s != '' && e['class2'].to_s == '' && e['class3'].to_s != ''
				class3_group_p << e['class3']
			else
				direct_group_p << e['name']
			end
		end
		class2_group_p = class2_group_p.uniq - class2_group
		class3_group_p = class3_group_p.uniq - class3_group

		# Classグループの作成
		tag_button = "<button type='button' class='btn btn-secondary btn-sm nav_button'"
		class2_group_p.each do |e| class_html << "#{tag_button} onclick=\"summonL3( '#{fg_key}:#{class1}:#{e}:#{class3}:#{food_name}', 3 )\">#{e.sub( '+', '' ).sub( /^.+\-/, '' )}</button>\n" end
		class3_group_p.each do |e| class_html << "#{tag_button} onclick=\"summonL3( '#{fg_key}:#{class1}:#{class2}:#{e}:#{food_name}', 3 )\">#{e.sub( '+', '' ).sub( /^.+\-/, '' )}</button>\n" end

		# ダイレクトグループの作成
		direct_html << make_direct_group( direct_group_p, name_his, fg_key, class1, class2, class3, 2, 1 )
	end

	# 擬似食品ボタンの作成
	pseudo_button = "<span onclick=\"pseudoAdd( 'init', '#{fg_key}:#{class1}:#{class2}:#{class3}:#{food_name}' )\">#{l[:plus]}</span>\n" if user.status > 0

	html = <<-"HTML"
	<h6>#{class_name.sub( '+', '' ).sub( /^.+\-/, '' )}</h6>
	#{class_html}
	#{direct_html}
	#{pseudo_button}
HTML

#### 第３層閲覧選択ページ
when 'fctb_l3'
	# 正規食品
	r = db.query( "SELECT * FROM #{$MYSQL_TB_TAG} WHERE FG='#{fg_key}' AND class#{class_no}='#{class_name}' AND status='9' GROUP BY SN;", false )
	r.each do |e|
		if e['class3'] != '' && e['class1'] != '' && e['class2'] != ''
			class3_group << e['class3']
		else
			direct_group << e['name']
		end
	end
	class3_group.uniq!

	# Class3グループの作成
	tag_button = "<button type='button' class='btn btn-info btn-sm nav_button'"
	class3_group.each do |e| class_html << "#{tag_button} onclick=\"summonL4( '#{fg_key}:#{class1}:#{class2}:#{e}:#{food_name}', 4 )\">#{e.sub( '+', '' ).sub( /^.+\-/, '' )}</button>\n" end

	# ダイレクトグループの作成
	direct_html = make_direct_group( direct_group, name_his, fg_key, class1, class2, class3, 0, 0 )

	# 擬似食品
	unless user.status == 0
		r = db.query( "SELECT * FROM #{$MYSQL_TB_TAG} WHERE FG='#{fg_key}' AND class#{class_no}='#{class_name}' AND (( user='#{user.name}' AND status='1' ) OR status='2' OR status='3' );", false )
		r.each do |e|
			if e['class3'].to_s != '' && e['class1'].to_s != '' && e['class2'].to_s != ''
				class3_group_p << e['class3']
			else
				direct_group_p << e['name']
			end
		end
		class3_group_p = class3_group_p.uniq - class3_group

		# Class3グループの作成
		tag_button = "<button type='button' class='btn btn-secondary btn-sm nav_button'"
		class3_group_p.each do |e| class_html << "#{tag_button} onclick=\"summonL4( '#{fg_key}:#{class1}:#{class2}:#{e}:#{food_name}', 4 )\">#{e.sub( '+', '' ).sub( /^.+\-/, '' )}</button>\n" end

		# ダイレクトグループの作成
		direct_html << make_direct_group( direct_group_p, name_his, fg_key, class1, class2, class3, 0, 1 )
	end

	# 擬似食品ボタンの作成
 	pseudo_button = "<span onclick=\"pseudoAdd( 'init', '#{fg_key}:#{class1}:#{class2}:#{class3}:#{food_name}' )\">#{l[:plus]}</span>\n" if user.status > 0

  html = <<-"HTML"
	<h6>#{class_name.sub( '+', '' ).sub( /^.+\-/, '' )}</h6>
	#{class_html}
	#{direct_html}
	#{pseudo_button}
HTML


#### 第４層閲覧選択ページ
when 'fctb_l4'
	# 正規食品
	r = db.query( "SELECT * FROM #{$MYSQL_TB_TAG} WHERE FG='#{fg_key}' AND class#{class_no}='#{class_name}' AND status='9' GROUP BY SN;", false )
	r.each do |e| direct_group << e['name'] end

	# ダイレクトグループの作成
	direct_html = make_direct_group( direct_group, name_his, fg_key, class1, class2, class3, 0, 0 )

	# 擬似食品
	unless user.status == 0
		r = db.query( "SELECT * FROM #{$MYSQL_TB_TAG} WHERE FG='#{fg_key}' AND class#{class_no}='#{class_name}' AND (( user='#{user.name}' AND status='1' ) OR status='2' OR status='3' );", false )
		r.each do |e| direct_group_p << e['name'] end

		# ダイレクトグループの作成
		direct_html << make_direct_group( direct_group_p, name_his, fg_key, class1, class2, class3, 0, 1 )
	end

	# 擬似食品ボタンの作成
 	pseudo_button = "<span onclick=\"pseudoAdd( 'init', '#{fg_key}:#{class1}:#{class2}:#{class3}:#{food_name}' )\">#{l[:plus]}</span>\n" if user.status > 0

	html = <<-"HTML"
	<h6>#{class_name.sub( '+', '' ).sub( /^.+\-/, '' )}</h6>
	#{direct_html}
	#{pseudo_button}
HTML

end

puts html
