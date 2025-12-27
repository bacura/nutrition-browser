#! /usr/bin/ruby
#encoding: utf-8
#Nutrition browser 2020 recipe list 0.4.7 (2025/07/06)
	

#==============================================================================
# STATIC
#==============================================================================
@debug = false
myself = File.basename( __FILE__ )
limit_num = 50

#==============================================================================
# LIBRARY
#==============================================================================
require './soul'
require './body'

#==============================================================================
# DEFINITION
#==============================================================================

# Language pack
def language_pack( language )
	l = Hash.new

	#Japanese
	l['ja'] = {
		recipel:	"レシピ帳",
		words:		"検索語：",
		norecipe:	"検索条件のレシピは見つかりませんでした",
		prevp:		"前項",
		nextp:		"次項",
		range:		"表示範囲",
		all:		"全て",
		all_ns:		"全て（ー調味系）",
		draft:		"仮組",
		protect:	"保護",
		public:		"公開",
		normal:		"無印",
		favoriter:	"お気に入り",
		publicou:	"公開(他ユーザー)",
		type:		"料理スタイル",
		role:		"献立区分",
		tech:		"調理区分",
		chomi:		"[ 調味％ ]",
		time:		"目安時間(分)",
		cost:		"目安費用(円)",
		limit:		"絞　り　込　み",
		reset:		"リセット",
		photo:		"写真",
		name:		"レシピ名",
		status:		"ステータス",
		display:	"表示数",
		delete:		"削除",
		pick:		"コードピック",
		com:		"コマンド",
		menu:		"お善＋",
		koyomi:		"こよみ＋",
		daughter:	"娘＋",
		import:		"取込",
		print:		"印刷",
		green:		"　　　",
		crosshair:	"<img src='bootstrap-dist/icons/crosshair.svg' style='height:2.0em; width:2.0em;'>",
		command:	"<img src='bootstrap-dist/icons/command.svg' style='height:1.2em; width:1.2em;'>",
		globe:		"<img src='bootstrap-dist/icons/globe.svg' style='height:1.2em; width:1.2em;'>",
		lock:		"<img src='bootstrap-dist/icons/lock-fill.svg' style='height:1.2em; width:1.2em;'>",
		cone:		"<img src='bootstrap-dist/icons/cone-striped.svg' style='height:1.2em; width:1.2em;'>",
		table:		"<img src='bootstrap-dist/icons/motherboard.svg' style='height:2.4em; width:2.4em;'>",
		calendar:	"<img src='bootstrap-dist/icons/calendar-plus.svg' style='height:2.4em; width:2.4em;'>",
		printer:	"<img src='bootstrap-dist/icons/printer.svg' style='height:2.4em; width:2.4em;'>",
		diagram:	"<img src='bootstrap-dist/icons/diagram-3.svg' style='height:2.4em; width:2.4em;'>",
		cp2words:	"<img src='bootstrap-dist/icons/eyedropper.svg' style='height:2.4em; width:2.4em;'>",
		trash:		"<img src='bootstrap-dist/icons/trash-red.svg' style='height:2.4em; width:2.4em;'>",
		root:		"<img src='bootstrap-dist/icons/person-circle.svg' style='height:1.2em; width:1.2em;'>",
		favorite:	"<img src='bootstrap-dist/icons/star-fill-y.svg' style='height:1.2em; width:1.2em;'>",
		space:		"　"
	}

	return l[language]
end


#### 表示範囲
def range_html( range, l )
	range_select = []
	7.times do |i| range_select[i] = $SELECT[range == i] end

	html = l[:range]
	html << '<select class="form-select form-select-sm" id="range">'
	html << "<option value='0' #{range_select[0]}>#{l[:all]}</option>"
	html << "<option value='1' #{range_select[1]}>#{l[:favoriter]}</option>"
	html << "<option value='2' #{range_select[2]}>#{l[:draft]}</option>"
	html << "<option value='3' #{range_select[3]}>#{l[:protect]}</option>"
	html << "<option value='4' #{range_select[4]}>#{l[:public]}</option>"
	html << "<option value='5' #{range_select[5]}>#{l[:normal]}</option>"
	html << "<option value='6' #{range_select[6]}>#{l[:publicou]}</option>"
	html << '</select>'

	return html
end


#### 料理スタイル生成
def type_html( type, l )
	html = l[:type]
	html << '<select class="form-select form-select-sm" id="type">'
	html << "<option value='99'>#{l[:all]}</option>"
	@recipe_type.size.times do |c|
		html << "<option value='#{c}' #{$SELECT[type == c]}>#{@recipe_type[c]}</option>"
	end
	html << '</select>'

	return html
end


#### 献立区分
def role_html( role, l )
	html = l[:role]
	html << '<select class="form-select form-select-sm" id="role">'
	html << "<option value='99'>#{l[:all]}</option>"
	html << "<option value='98' #{$SELECT[role == 98]}>#{l[:all_ns]}</option>"
	@recipe_role.size.times do |c|
		html << "<option value='#{c}' #{$SELECT[role == c]}>#{@recipe_role[c]}</option>"
	end
	html << "<option value='100' #{$SELECT[role == 100]}>#{l[:chomi]}</option>"
	html << '</select>'

	return html
end


#### 調理区分
def tech_html( tech, l )
	html = l[:tech]
	html << '<select class="form-select form-select-sm" id="tech">'
	html << "<option value='99'>#{l[:all]}</option>"
	@recipe_tech.size.times do |c|
		html << "<option value='#{c}' #{$SELECT[tech == c]}>#{@recipe_tech[c]}</option>"
	end
	html << '</select>'

	return html
end


#### 目安時間
def time_html( time, l )
	html = l[:time]
	html << '<select class="form-select form-select-sm" id="time">'
	html << "<option value='99'>#{l[:all]}</option>"
	@recipe_time.size.times do |c|
		html << "<option value='#{c}' #{$SELECT[time == c]}>#{@recipe_time[c]}</option>"
	end
	html << '</select>'

	return html
end


#### 目安費用
def cost_html( cost, l )
	html = l[:cost]
	html << '<select class="form-select form-select-sm" id="cost">'
	html << "<option value='99'>#{l[:all]}</option>"
	@recipe_cost.size.times do |c|
		html << "<option value='#{c}' #{$SELECT[cost == c]}>#{@recipe_cost[c]}</option>"
	end
	html << '</select>'

	return html
end


#### ページングパーツ
def pageing_html( page, page_start, page_end, page_max, l )
	html = ''
	html << '<ul class="pagination pagination-sm justify-content-end">'
	if page == 1
		html << "<li class='page-item disabled'><span class='page-link'>#{l[:prevp]}</span></li>"
	else
		html << "<li class='page-item'><span class='page-link' onclick=\"recipeListP( #{page - 1} )\">#{l[:prevp]}</span></li>"
	end
	html << "<li class='page-item'><a class='page-link' onclick=\"recipeListP( '1' )\">1…</a></li>" unless page_start == 1

	page_start.upto( page_end ) do |c|
		active = ''
		active = ' active' if page == c
		html << "<li class='page-item#{active}'><a class='page-link' onclick=\"recipeListP( #{c} )\">#{c}</a></li>"
	end
	html << "<li class='page-item active'><a class='page-link' onclick=\"recipeListP( 1 )\">1</a></li>" if page_end == 0

	html << "<li class='page-item'><a class='page-link' onclick=\"recipeListP( '#{page_max}' )\">…#{page_max}</a></li>" unless page_end == page_max
	if page == page_max
		html << "<li class='page-item disabled'><span class='page-link'>#{l[:nextp]}</span></li>"
	else
		html << "<li class='page-item'><span class='page-link' onclick=\"recipeListP( #{page + 1} )\">#{l[:nextp]}</span></li>"
	end
	html << '  </ul>'

	return html
end


def referencing( words, db, sql_where_ij )
	words.gsub!( /\s+/, "\t")
	words.gsub!( /　+/, "\t")
	words.gsub!( /,+/, "\t")
	words.gsub!( /、+/, "\t")
	words.gsub!( /\t{2,}/, "\t")
	query_word = words.split( "\t" )
	query_word.uniq!

	# Recoding query & converting by DIC
	true_query = []
	query_word.each do |e|
		db.query( "INSERT INTO #{$TB_SLOGR} SET user=?, words=?, date=?", true, [db.user.name, e, @datetime] )
		res = db.query( "SELECT * FROM #{$TB_DIC} WHERE alias=?", false, [e] )&.first
		if res
			res2 = db.query( "SELECT * FROM #{$TB_TAG} WHERE class1=? OR class2=? OR class3=?", false, [res['org_name'], res['org_name'], res['org_name']] )&.first
			if res2
				res2.each do |ee| true_query << ee['name'] end
			else
				true_query << res['org_name']
			end
		else
			true_query << e
		end
	end
	true_query.uniq!

	if @debug
		puts "query_word:#{query_word}<br>"
		puts "true_query:#{true_query}<br>"
		puts "<hr>"
	end

	# Referencing recipe
	true_query.each do |e|
		if e =~ /\-r\-/
			return db.query( "SELECT * FROM #{$TB_RECIPE} WHERE code=? AND ( user=? OR public='1' );", false, [e, db.user.name] )
		else
			return db.query( "SELECT t1.* FROM #{$TB_RECIPE} AS t1 INNER JOIN #{$TB_RECIPEI} AS t2 ON t1.code = t2.code #{sql_where_ij} AND t2.word='#{e}';", false )
		end
	end
end


def recipe_line( recipe, user, page, color, l )
	html = "<tr style='font-size:medium; background-color:#{color};' oncontextmenu=\"modalTip( '#{recipe.code}' )\">"

	if recipe.media[0] != nil
		html << "<td><img src='#{$PHOTO}/#{recipe.media[0]}-tns.jpg' class='photo_tns' onclick=\"modalPhoto( '#{recipe.media[0]}' )\"></td>"
	else
		html << "<td>-</td>"
	end

	tags =''
	recipe.tag().each do |e| tags << "&nbsp;<span class='list_tag badge bbg' onclick=\"searchDR( '#{e}' )\">#{e}</span>" end
	if user.status >= 1
		html << "<td onclick=\"initCB( 'load', '#{recipe.code}', '#{recipe.user.name}' )\">#{recipe.name}</td><td>#{tags}</td>"
	else
		html << "<td><a href='login.cgi'>#{recipe.name}</a></td><td>#{tags}</td>"
	end

	html << "<td>"
	html << ( recipe.favorite == 1 ? l[:favorite] : l[:space] )
	html << ( recipe.public   == 1 ? l[:globe]    : l[:space] )
	html << ( recipe.protect  == 1 ? l[:lock]     : l[:space] )
	html << ( recipe.draft    == 1 ? l[:cone]     : l[:space] )
	html << "</td>"

	html << "<td onclick=\"modalTip( '#{recipe.code}' )\">#{l[:command]}</td>"
	html << "</tr>"

	return html
end

#==============================================================================
# Main
#==============================================================================

user = User.new( @cgi )
l = language_pack( user.language )
db = Db.new( user, @debug, false )
cfg = Config.new( user, 'recipe-list' )

res = db.query( "SELECT icache FROM cfg WHERE user=?", false, [user.name] )&.first
if res
	if res['icache'].to_i == 1
		html_init_cache( nil )
	else
		html_init( nil )
	end
else
	html_init_cache( nil )
end

cfg.val['page'] = cfg.val['page'].to_i == 0 ? 1 : cfg.val['page'].to_i
cfg.val['page_limit'] = cfg.val['page_limit'].nil? ? limit_num : cfg.val['page_limit'].to_i
cfg.val['range'] = cfg.val['range'].nil?  ? 0 : cfg.val['range'].to_i
cfg.val['type'] = cfg.val['type'].nil? ? 99 : cfg.val['type'].to_i
cfg.val['role'] = cfg.val['role'].nil? ? 99 : cfg.val['role'].to_i
cfg.val['tech'] = cfg.val['tech'].nil? ? 99 : cfg.val['tech'].to_i
cfg.val['time'] = cfg.val['time'].nil? ? 99 : cfg.val['time'].to_i
cfg.val['cost'] = cfg.val['cost'].nil? ? 99 : cfg.val['cost'].to_i
cfg.val['family'] = cfg.val['family'].nil? ? 0 : cfg.val['family'].to_i
cfg.val['words'] = cfg.val['words'].nil? ? '' : cfg.val['words'].to_s

#### POST
command = @cgi['command']
code = @cgi['code']
if @debug
	puts "command: #{command}<br>"
	puts "code: #{code}<br>"
	puts "<hr>"
end


ref_msg = ''
case command
when 'reset'
	cfg.val['page'] = 1
	cfg.val['page_limit'] = limit_num
	cfg.val['range'] = 0
	cfg.val['type'] = 99
	cfg.val['role'] = 99
	cfg.val['tech'] = 99
	cfg.val['time'] = 99
	cfg.val['cost'] = 99
	cfg.val['family'] = 0
	cfg.val['words'] = ''

	cfg.val['green'] = 0

when 'green_set'
	cfg.val['page'] = 1
	cfg.val['page_limit'] = @cgi['page_limit'].to_i
	cfg.val['range'] = @cgi['range'].to_i
	cfg.val['type'] = @cgi['type'].to_i
	cfg.val['role'] = @cgi['role'].to_i
	cfg.val['tech'] = @cgi['tech'].to_i
	cfg.val['time'] = @cgi['time'].to_i
	cfg.val['cost'] = @cgi['cost'].to_i
	cfg.val['family'] = @cgi['family'].to_i
	cfg.val['words'] = @cgi['words']

	cfg.val['green'] = 1
	cfg.val['gb_page_limit'] = cfg.val['page_limit']
	cfg.val['gb_range'] = cfg.val['range']
	cfg.val['gb_type'] = cfg.val['type']
	cfg.val['gb_role'] = cfg.val['role']
	cfg.val['gb_tech'] = cfg.val['tech']
	cfg.val['gb_time'] = cfg.val['time']
	cfg.val['gb_cost'] = cfg.val['cost']
	cfg.val['gb_family'] = cfg.val['family']
	cfg.val['gb_words'] = cfg.val['words']

when 'green_return'
	cfg.val['page'] = 1
	cfg.val['page_limit'] = cfg.val['gb_page_limit'].to_i
	cfg.val['range'] = cfg.val['gb_range'].to_i
	cfg.val['type'] = cfg.val['gb_type'].to_i
	cfg.val['role'] = cfg.val['gb_role'].to_i
	cfg.val['tech'] = cfg.val['gb_tech'].to_i
	cfg.val['time'] = cfg.val['gb_time'].to_i
	cfg.val['cost'] = cfg.val['gb_cost'].to_i
	cfg.val['family'] =cfg.val['gb_family'].to_i
	cfg.val['words'] = cfg.val['gb_words']

when 'delete'
	puts "Deleting photos<br>" if @debug
	if user.status != 7
		puts "Deleting media from DB, Real<br>" if @debug
		target_media = Media.new( user )
		target_media.origin = code
		target_media.get_series()
		target_media.delete_series( true )

		puts "Deleting recipe from DB<br>" if @debug
		recipe = Recipe.new( user )
		recipe.code = code
		recipe.delete_db

		puts "Clearing Sum<br>" if @debug
		res = db.query( "SELECT code FROM #{$TB_SUM} WHERE user=?", false, [user.name] )&.first
		db.query( "UPDATE #{$TB_SUM} SET code='', name='', dish=1 WHERE user=?", true, [user.name] ) if res['code'] == code
	end
when 'subspecies'
	# Loading original recipe
	if user.status != 7
		recipe = Recipe.new( user )
		recipe.load_db( code, true )

		# Copying phots
		new_media_code = generate_code( user.name, 'p' )
		new_recipe_code = generate_code( user.name, 'r' )

		source_media = Media.new( user )
		source_media.origin = code
		source_media.get_series()

		source_media.series.each do |e|
			FileUtils.cp( "#{$PHOTO_PATH}/#{e}-tns.jpg", "#{$PHOTO_PATH}/#{new_media_code}-tns.jpg" ) if File.exist?( "#{$PHOTO_PATH}/#{e['code']}-tns.jpg" )
			FileUtils.cp( "#{$PHOTO_PATH}/#{e}-tn.jpg", "#{$PHOTO_PATH}/#{new_media_code}-tn.jpg" ) if File.exist?( "#{$PHOTO_PATH}/#{e['code']}-tn.jpg" )
			FileUtils.cp( "#{$PHOTO_PATH}/#{e}-tn.jpg", "#{$PHOTO_PATH}/#{new_media_code}.jpg" ) if File.exist?( "#{$PHOTO_PATH}/#{e['code']}-tn.jpg" )
			
			new_media = Media.new( user )
			new_media.origin = new_recipe_code
			new_media.code = new_media_code
			new_media.date = @datetime
			new_media.base = 'recipe'
			new_media.alt = recipe.name
			new_media.save_db()
		end

		# Insertinbg recipe into DB
		recipe.user.name = user.name
		recipe.code = new_recipe_code
		recipe.favorite = 0
		recipe.public = 0
		recipe.protect = 0
		recipe.draft = 1
		recipe.date = @datetime
		recipe.root = code
		recipe.insert_db
	end

when 'limit', 'refer'
	cfg.val['page'] = ( @cgi['page'].to_i == 0 || command == 'refer' ) ? 1 : @cgi['page'].to_i
	cfg.val['page_limit'] = @cgi['page_limit'].to_i == 0 ? limit_num : @cgi['page_limit'].to_i
	cfg.val['range'] = @cgi['range'].to_i
	cfg.val['type'] = command == 'limit' ? @cgi['type'].to_i : 99
	cfg.val['role'] = command == 'limit' ? @cgi['role'].to_i : 99
	cfg.val['tech'] = command == 'limit' ? @cgi['tech'].to_i : 99
	cfg.val['time'] = command == 'limit' ? @cgi['time'].to_i : 99
	cfg.val['cost'] = command == 'limit' ? @cgi['cost'].to_i : 99
	cfg.val['family'] = command == 'limit' ? @cgi['family'].to_i : 99
	cfg.val['words'] = @cgi['words']

when 'modal_body'
	cfg.val['page'] = @cgi['page'].to_i == 0 ? 1 : @cgi['page'].to_i
	recipe = Recipe.new( user )
    recipe.load_db( code, true )

    puts recipe.name

	puts "<table class='table table-borderless'><tr>"

	if user.status >= 1 && recipe.user.name == user.name
		puts "<td align='center' onclick=\"addingMT( '#{recipe.code}', '#{recipe.name}' )\">#{l[:table]}<br><br>#{l[:menu]}</td>"
	end

	if user.status >= 2 && recipe.user.name == user.name
		puts "<td align='center' onclick=\"addKoyomi( '#{recipe.code}' )\">#{l[:calendar]}<br><br>#{l[:koyomi]}</td>"
	end

	puts "<td align='center' onclick=\"print_templateSelect( '#{recipe.code}' )\">#{l[:printer]}<br><br>#{l[:print]}</td>"

	if user.status >= 1 && recipe.user.name == user.name && ( recipe.root == nil || recipe.root == '' )
		puts "<td align='center' onclick=\"recipeImport( 'subspecies', '#{recipe.code}', '#{cfg.val['page']}' )\">#{l[:diagram]}<br><br>#{l[:daughter]}</td>"
	elsif user.status >= 1 && recipe.user.name == user.name
		puts "<td align='center' onclick=\"initCB( 'load', '#{recipe.root}', '#{recipe.user.name}' )\">#{l[:root]}<br><br>#{l[:import]}</td>"
	end

	if user.status >= 1 && recipe.user.name == user.name
		puts "<td align='center' onclick=\"cp2words( '#{recipe.code}', '' )\">#{l[:cp2words]}<br><br>#{l[:pick]}</td>"
	end

	if recipe.user.name == user.name && recipe.protect == 0
		puts "<td align='center' ><input type='checkbox' id='#{recipe.code}'>&nbsp;<span onclick=\"recipeDelete( '#{recipe.code}', #{cfg.val['page']} )\">#{l[:trash]}</span><br><br>#{l[:delete]}</td>"
	end

	puts '</tr></table>'

	exit
end

cfg.val['range'] = 5 if user.status == 0
p cfg.val if @debug


#### WHERE setting
sql_where = 'WHERE '
sql_where_ij = 'WHERE '
case cfg.val['range']
# 自分の全て
when 0
	sql_where << " user='#{user.name}' AND name!=''"
	sql_where_ij << " t1.user='#{user.name}' AND t1.name!=''"
# 自分のお気に入り
when 1
	sql_where << "user='#{user.name}' AND name!='' AND favorite='1'"
	sql_where_ij << "t1.user='#{user.name}' AND t1.name!='' AND t1.favorite='1'"
# 自分の下書き
when 2
	sql_where << "user='#{user.name}' AND name!='' AND draft='1'"
	sql_where_ij << "t1.user='#{user.name}' AND t1.name!='' AND t1.draft='1'"
# 自分の保護
when 3
	sql_where << "user='#{user.name}' AND protect='1' AND name!=''"
	sql_where_ij << "t1.user='#{user.name}' AND t1.protect='1' AND t1.name!=''"
# 自分の公開
when 4
	sql_where << "user='#{user.name}' AND public='1' AND name!=''"
	sql_where_ij << "t1.user='#{user.name}' AND t1.public='1' AND t1.name!=''"
# 自分の無印
when 5
	sql_where << "user='#{user.name}' AND public='0' AND draft='0' AND name!=''"
	sql_where_ij << "t1.user='#{user.name}' AND t1.public='0' AND t1.draft='0' AND t1.name!=''"
# 他の公開
when 6
	sql_where << "public='1' AND user!='#{user.name}' AND name!=''"
	sql_where_ij << "t1.public='1' AND t1.user!='#{user.name}' AND t1.name!=''"
else
	sql_where << " user='#{user.name}' AND name!=''"
	sql_where_ij << " t1.user='#{user.name}' AND t1.name!=''"
end

sql_where << " AND type='#{cfg.val['type']}'" unless cfg.val['type'] == 99
if cfg.val['role'] == 98
	sql_where << " AND role!='100' AND role!='7'"
elsif cfg.val['role'] != 99
	sql_where << " AND role='#{cfg.val['role']}'"
end
sql_where << " AND tech='#{cfg.val['tech']}'" unless cfg.val['tech'] == 99
sql_where << " AND time>0 AND time<=#{cfg.val['time']}" unless cfg.val['time'] == 99
sql_where << " AND cost>0 AND cost<=#{cfg.val['cost']}" unless cfg.val['cost'] == 99

sql_where_ij << " AND t1.type='#{cfg.val['type']}'" unless cfg.val['type'] == 99
if cfg.val['role'] == 98
	sql_where_ij << " AND t1.role!='100' AND t1.role!='7'"
elsif cfg.val['role'] != 99
	sql_where_ij << " AND t1.role='#{cfg.val['role']}'"
end
sql_where_ij << " AND t1.tech='#{cfg.val['tech']}'" unless cfg.val['tech'] == 99
sql_where_ij << " AND t1.time>0 AND t1.time<=#{cfg.val['time']}" unless cfg.val['time'] == 99
sql_where_ij << " AND t1.cost>0 AND t1.cost<=#{cfg.val['cost']}" unless cfg.val['cost'] == 99


#### 検索条件HTML
html_range = range_html( cfg.val['range'], l )
html_type = type_html( cfg.val['type'], l )
html_role = role_html( cfg.val['role'], l )
html_tech = tech_html( cfg.val['tech'], l )
html_time = time_html( cfg.val['time'], l )
html_cost = cost_html( cfg.val['cost'], l )


puts "Recipe list<br>" if @debug
recipes = []
recipe_num = 0
res = nil
ref_msg = cfg.val['words']

if cfg.val['words'].to_s != ''
	if /\-r\-/ =~ cfg.val['words'].to_s
		res = db.query( "SELECT * FROM #{$TB_RECIPE} WHERE code='#{cfg.val['words'].to_s}';", false )
		ref_msg = res.first['name']
	else
		res = referencing( cfg.val['words'], db, sql_where_ij )
		offset = ( cfg.val['page'] - 1 ) * cfg.val['page_limit']
		cfg.val['page_limit'] = offset + cfg.val['page_limit']
	end
	recipe_num = res.size
	ref_msg = "#{l[:words]}#{cfg.val['words']}<br>#{l[:norecipe]}" if res.size == 0
else
	r = db.query( "SELECT COUNT(*) FROM #{$TB_RECIPE} #{sql_where};", false )
	recipe_num = r.first['COUNT(*)']
	offset = ( cfg.val['page'] - 1 ) * cfg.val['page_limit']
	res = db.query( "SELECT * FROM #{$TB_RECIPE} #{sql_where} ORDER BY name LIMIT #{offset}, #{cfg.val['page_limit']};", false )

end

res.each do |e|
	o = Recipe.new( user )
	o.load_db( e, false )
	o.load_media
	recipes << o
end


puts "Paging parts<br>" if @debug
page_max = recipe_num / cfg.val['page_limit']
page_start = 1
page_max += 1 if ( recipe_num % cfg.val['page_limit'] ) != 0
page_end = page_max

if page_end > 5
	if cfg.val['page'] > 3
		page_start = cfg.val['page'] - 3
		page_start = page_max - 6 if page_max - page_start < 7
	end
	if page_end - cfg.val['page'] < 3
		page_end = page_max
	else
		page_end = cfg.val['page'] + 3
		page_end = 7 if page_end < 7
	end
else
	page_end = page_max
end
html_paging = pageing_html( cfg.val['page'], page_start, page_end, page_max, l )


puts "families<br>" if @debug
family_pair = Hash.new
family_recipes = Hash.new

if cfg.val['family'] == 1
	recipes.each do |e|
		r = db.query( "SELECT code FROM #{$TB_RECIPE} WHERE user=? and root=? ORDER BY name;", false, [user.name, e.code] )
		daughters = []
		daughter_recipes = []
		r.each do |ee|
			daughters << ee['code']

			ro = Recipe.new( user )
      		ro.load_db( ee['code'], true )
			daughter_recipes << ro
		end
		if daughters.size > 0
			family_pair[e.code] = daughters
			family_recipes[e.code] = daughter_recipes
		end
	end
end


puts "Recipe HTML parts<br>" if @debug
recipe_html = ''
recipes.each do |e|
	if cfg.val['family'] == 1
		if e.root == '' && family_pair[e.code] == nil
			recipe_html << recipe_line( e, user, cfg.val['page'], 'aliceblue', l )
		elsif family_pair.key?( e.code )
			recipe_html << recipe_line( e, user, cfg.val['page'], 'lavender', l )
			family_recipes[e.code].each do |ee|
				recipe_html << recipe_line( ee, user, cfg.val['page'], 'snow', l )
			end
		end
	else
		recipe_html << recipe_line( e, user, cfg.val['page'], 'aliceblue', l )
	end
end


puts "Page limit HTML parts<br>" if @debug
page_limit_html = ''
nums = [25, 50, 75, 100, 150, 200]
nums.each do |e|
	page_limit_html << "<option value='#{e}' #{$SELECT[ e == cfg.val['page_limit']]}>#{e}</option>"
end

puts "Green button HTML parts<br>" if @debug
if cfg.val['green'] == 1
	green_button = "<button class='btn btn-success btn-sm gb' type='button' onclick='recipeListGreen( \"green_return\" )'>#{l[:green]}</button>"
else
	green_button = "<button class='btn btn-success btn-sm' type='button' onclick='recipeListGreen( \"green_set\" )'>#{l[:green]}</button>"
end


puts "HTML<br>" if @debug
html = <<~"HTML"
<div class='container-fluid'>
	<div class='row'>
		<div class='col-5'><h5>#{l[:recipel]}&nbsp;(#{recipe_num}) #{ref_msg}</h5></div>
		<div class='col-2' align='center'><span onclick='recipe3ds()'>#{l[:crosshair]}</span></div>
		<div class='col-5' align='right'>#{html_paging}</div>
	</div>
	<br>
	<div class='row'>
		<div class='col'>#{html_range}</div>
		<div class='col'>#{html_type}</div>
		<div class='col'>#{html_role}</div>
		<div class='col'>#{html_tech}</div>
		<div class='col'>#{html_time}</div>
		<div class='col'>#{html_cost}</div>
	</div><br>
	<div class='row'>
		<div class='col-1'>
			<div class="form-check">
	  			<input class="form-check-input" type="checkbox" id="family" #{$CHECK[cfg.val['family']]}>
	  			<label class='form-check-label'>#{l[:diagram]}</label>
			</div>
		</div>
		<div class='col-9'>
			<div class='row'><button class="btn btn-info btn-sm" type="button" onclick="recipeListP( '#{cfg.val['page']}' )">#{l[:limit]}</button></div>
		</div>
		<div class='col-1'>
			#{green_button}
		</div>
		<div class='col-1'>
			<button class="btn btn-warning btn-sm" type="button" onclick="recipeList( 'reset' )">#{l[:reset]}</button>
		</div>
	</div>
	<br>

	<table class="table table-sm table-hover">
		<thead class="table-light">
			<tr>
				<td>#{l[:photo]}</td>
				<td>#{l[:name]}</td>
				<td></td>
				<td>#{l[:status]}</td>
				<td>#{l[:com]}</td>
			</tr>
		</thead>
			#{recipe_html}
	</table>

	<div class='row'>
		<div class='col-2'>
			<div class="input-group input-group-sm">
				<label class="input-group-text" for="page_limit">#{l[:display]}</label>
				<select class="form-select form-select-sm" id='page_limit'>
					#{page_limit_html}
				</select>
			</div>
		</div>
		<div class='col-5'>
		</div>
		<div class='col-5'>#{html_paging}</div>
	</div>
</div>
HTML

puts html



#==============================================================================
# POST PROCESS
#==============================================================================
#### 検索設定の保存
p cfg.val if @debug
cfg.update()


#==============================================================================
# FRONT SCRIPT START
#==============================================================================

if command == 'init' || command == 'refer' 
	js = <<-"JS"
<script type='text/javascript'>
var postReq_recipel = async (command, requestData, successCallback) => {
    try {
        const response = await fetch('recipel.cgi', {
            method: 'POST',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            body: new URLSearchParams({ command, ...requestData }),
        });
        if (!response.ok) {
            const text = await response.text();
            console.error(`Request failed: HTTP ${response.status}, ${text}`);
            alert("An error occurred. Please try again.");
            return;
        }
        const responseData = await response.text();
        successCallback(responseData);
    } catch (error) {
        console.error('Request failed:', error);
        alert("An error occurred. Please try again.");
    }
};

// Displaying recipe list with narrow down
var recipeListP = async (page) => {
    const range = $("#range").val();
    const type = $("#type").val();
    const role = $("#role").val();
    const tech = $("#tech").val();
    const time = $("#time").val();
    const cost = $("#cost").val();
    const words = $("#words").val();
    const page_limit = $("#page_limit").val();
    const family = $("#family").is(":checked") ? 1 : 0;
    await postReq_recipel('limit', { range, type, role, tech, time, cost, page, words, family, page_limit }, data => {
        $("#L1").html(data);
    });
};

// Green button
var recipeListGreen = async (com) => {
    const range = $("#range").val();
    const type = $("#type").val();
    const role = $("#role").val();
    const tech = $("#tech").val();
    const time = $("#time").val();
    const cost = $("#cost").val();
    const words = $("#words").val();
    const page_limit = $("#page_limit").val();
    const family = $("#family").is(":checked") ? 1 : 0;
    await postReq_recipel(com, { range, type, role, tech, time, cost, words, family, page_limit }, data => {
        $("#L1").html(data);
    });
};

// Displaying recipe list after delete
var recipeDelete = async (code, page) => {
    const range = $("#range").val();
    const type = $("#type").val();
    const role = $("#role").val();
    const tech = $("#tech").val();
    const time = $("#time").val();
    const cost = $("#cost").val();
    const page_limit = $("#page_limit").val();
    const family = $("#family").is(":checked") ? 1 : 0;

    if ($("#" + code).is(":checked")) {
        await postReq_recipel('delete', { code, range, type, role, tech, time, cost, page, family, page_limit }, async () => {
            await postReq_recipel('limit', { range, type, role, tech, time, cost, page, family, page_limit }, data => {
                $("#L1").html(data);
                displayVIDEO('Removed');
                const modalElement = document.querySelector('#modal_tip');
                if (modalElement) {
                    const modal = bootstrap.Modal.getInstance(modalElement) || new bootstrap.Modal(modalElement);
                    modal.hide();
                }
            });
        });
    } else {
        displayVIDEO('Check! (>_<)');
    }
};

// Generating subSpecies
var recipeImport = async (com, code, page) => {
    const range = $("#range").val();
    const type = $("#type").val();
    const role = $("#role").val();
    const tech = $("#tech").val();
    const time = $("#time").val();
    const cost = $("#cost").val();
    const page_limit = $("#page_limit").val();
    const family = $("#family").is(":checked") ? 1 : 0;

    await postReq_recipel(com, { code, range, type, role, tech, time, cost, page, family, page_limit }, data => {
        $( "#L1" ).html( data );
        displayVIDEO( 'Recipe has branched' );
        const modalElement = document.querySelector( '#modal_tip' );
        if ( modalElement ) {
            const modal = bootstrap.Modal.getInstance( modalElement ) || new bootstrap.Modal( modalElement );
            modal.hide();
        }
    });
};

// Modal Tip for fcz list
var modalTip = async (code) => {
    postLayer( '#{myself}', 'modal_body', true, 'modal_tip_body', { code });

    const modalElement = document.querySelector( '#modal_tip' );
    const modal = new bootstrap.Modal( modalElement );
    modal.show();
};

</script>
JS

end

puts js
puts '(^q^)' if @debug
