#! /usr/bin/ruby
#encoding: utf-8
#Nutrition browser 2020 menu list 0.0.6 (2025/01/04)


#==============================================================================
#STATIC
#==============================================================================
page_limit = 20
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
		menul: 		'献立一覧',
		range: 		'表示範囲',
		label: 		'ラベル',
		limit: 		'絞　り　込　み',
		reset: 		'リセット',
		photo: 		'写真',
		menu_name: 	'献立名',
		extend_num: '展開数',
		operation: 	'操作',
		all: 		'全て',
		public: 	'公開',
		publico: 	'公開（他）',
		normal: 	'常食',
		prev: 		'前頁',
		next: 		'次頁',
		protect: 	'保護',
		status: 	'ステータス',
		trash: 		"<img src='bootstrap-dist/icons/trash.svg' style='height:1.2em; width:1.2em;'>",
		download: 	"<img src='bootstrap-dist/icons/box-arrow-in-down.svg' style='height:1.2em; width:1.2em;'>",
		calendar: 	"<img src='bootstrap-dist/icons/calendar-plus.svg' style='height:1.2em; width:1.2em;'>",
		globe: 		"<img src='bootstrap-dist/icons/globe.svg' style='height:1.2em; width:1.2em;'>",
		lock: 		"<img src='bootstrap-dist/icons/lock-fill.svg' style='height:1.2em; width:1.2em;'>"
	}

	return l[language]
end


### HTML display range
def range_html( range, l )
	html = '<select class="form-select form-select-sm" id="range">'
	html << "<option value='0' #{$SELECT[range == 0]}>#{l[:all]}</option>"
	html << "<option value='1' #{$SELECT[range == 1]}>#{l[:protect]}</option>"
	html << "<option value='2' #{$SELECT[range == 2]}>#{l[:public]}</option>"
	html << "<option value='3' #{$SELECT[range == 3]}>#{l[:publico]}</option>"
	html << '</select>'

	return html
end


#### HTML of label
def label_html( db, label, l )
	r = db.query( "SELECT label FROM #{$TB_MENU} WHERE user='#{db.user.name}' AND name!='';", false )

	label_list = r.map { |e| e['label'] }.uniq

	html = '<select class="form-select form-select-sm" id="label_list">'
	html << "<option value='#{l[:all]}' id='normal_label_list0' style='display:inline'>#{l[:all]}</option>"
	normal_label_c = 0
	label_list.each do |e|
		unless e == l[:all]
			normal_label_c += 1
			html << "<option value='#{e}' id='normal_label_list#{normal_label_c}' style='display:inline' #{$SELECT[e == label]}>#{e}</option>"
		end
	end

	school_flavor = ''
	if db.user.status >= 5 && db.user.status != 6
		school_label_c = 0
		r = db.query( "SELECT label FROM #{$TB_SCHOOLM} WHERE user='#{db.user.name}';", false )
		r.each do |e|
			if e['label'] != nil
				school_flavor = 'btn-info'
				a = e['label'].split( "\t" )
				a.each do |ee|
					school_label_c += 1
					html << "<option value='#{ee}' id='school_label_list#{school_label_c}' style='display:none' #{$SELECT[ee == label]}>#{ee}</option>"
				end
			end
		end
	end
	html << '</select>'

	return html, normal_label_c, school_label_c, school_flavor
end


#### HTML of Paging
def pageing_html( page, page_start, page_end, page_max, l )
	html = ''
	html << '<ul class="pagination pagination-sm justify-content-end">'
	if page == 1
		html << "<li class='page-item disabled'><span class='page-link'>#{l[:prev]}</span></li>"
	else
		html << "<li class='page-item'><span class='page-link' onclick=\"changeMenuPage( #{page - 1} )\">#{l[:prev]}</span></li>"
	end
	unless page_start == 1
		html << "<li class='page-item'><a class='page-link' onclick=\"changeMenuPage( '1' )\">1…</a></li>"
	end
	page_start.upto( page_end ) do |c|
		active = ''
		active = ' active' if page == c
		html << "<li class='page-item#{active}'><a class='page-link' onclick=\"changeMenuPage( #{c} )\">#{c}</a></li>"
	end
	unless page_end == page_max
		html << "<li class='page-item'><a class='page-link' onclick=\"changeMenuPage( '#{page_max}' )\">…#{page_max}</a></li>"
	end
	if page == page_max
		html << "<li class='page-item disabled'><span class='page-link'>#{l[:next]}</span></li>"
	else
		html << "<li class='page-item'><span class='page-link' onclick=\"changeMenuPage( #{page + 1} )\">#{l[:next]}</span></li>"
	end
	html << '  </ul>'

	return html
end
#==============================================================================
# Main
#==============================================================================
user = User.new( @cgi )
l = language_pack( user.language )
db = Db.new( user, @debug, false )

r = db.query( "SELECT icache, menul FROM cfg WHERE user='#{user.name}';", false )
if r.first
	if r.first['icache'].to_i == 1
		html_init_cache( nil )
	else
		html_init( nil )
	end
else
	html_init_cache( nil )
end
user.debug if @debug

#### Getting POST data
command = @cgi['command']
code = @cgi['code']
page = @cgi['page'].to_i
range = @cgi['range'].to_i
label = @cgi['label']
if @debug
	puts "command: #{command}<br>"
	puts "code: #{code}<br>"
	puts "page: #{page}<br>"
	puts "Range: #{range}<br>"
	puts "Label: #{label}<br>"
	puts "<hr>"
end


#### Getting page
case command
when 'init'
	r = db.query( "SELECT menul FROM #{$TB_CFG} WHERE user='#{user.name}';", false )
	if r.first
		if r.first['menul'] != nil
			a = r.first['menul'].split( ':' )
			page = a[0].to_i
			range = a[1].to_i
			label = a[2]
		end
	end
when 'delete'
	puts 'Deleting menu' if @debug
	r = db.query( "SELECT code FROM #{$TB_MEDIA} WHERE user='#{user.name}' and orign='#{code}';", false )
	r.each do |e|
		File.unlink "#{$PHOTO_PATH}/#{e.code}-tns.jpg" if File.exist?( "#{$PHOTO_PATH}/#{e.code}-tns.jpg" )
		File.unlink "#{$PHOTO_PATH}/#{e.code}-tn.jpg" if File.exist?( "#{$PHOTO_PATH}/#{e.code}-tn.jpg" )
		File.unlink "#{$PHOTO_PATH}/#{e.code}.jpg" if File.exist?( "#{$PHOTO_PATH}/#{e.code}.jpg" )
	end

	#レシピデータベースのの更新（削除）
	menu = Menu.new( user )
	menu.code = code
	menu.delete_db

	mt = Tray.new( user )
	if mt.code == code
		mt.code = ''
		mt.name = ''
		mt.update_db
	end

when 'import'
#### 献立のインポート
#### 不完全
	# インポート元の読み込み
	r = db.query( "SELECT * FROM #{$TB_MENU} WHERE code='#{code}';", false )

	if r.first
		#レシピデータベースのの更新(新規)
		new_code = generate_code( user.name, 'm' )
#		db.query("INSERT INTO #{$TB_MENU} SET code='#{new_code}', user='#{user.name}', public='0', name='*#{r.first['name']}', type='#{r.first['type']}', role='#{r.first['role']}', tech='#{r.first['tech']}', time='#{r.first['time']}', cost='#{r.first['cost']}', sum='#{r.first['sum']}', protocol='#{r.first['protocol']}', fig1='0', fig2='0', fig3='0', date='#{$DATETIME}';", false, @debug )
	end
end

page = 1 if page < 1
label ||= ''

puts "WHERE setting<br>" if @debug
sql_where = "WHERE "
case range
when 1
	sql_where << "user='#{user.name}' AND protect=1"
when 2
	sql_where << "user='#{user.name}' AND name!='' AND public=1"
when 3
	sql_where << "user!='#{user.name}' AND name!='' AND public=1"
else
	sql_where << "user='#{user.name}' AND name!=''"
end
sql_where << " AND label='#{label}'" unless label == '' || label == l[:all]


puts "HTML range<br>" if @debug
html_range = range_html( range, l )


puts "HTML label<br>" if @debug
html_label, normal_label_c, school_label_c, school_flavor = label_html( db, label, l )


puts "Menu list<br>" if @debug
menus = []
r = db.query( "SELECT * FROM #{$TB_MENU} #{sql_where} ORDER BY name;", false )
r.each do |e|
	o = Menu.new( user )
	o.load_db( e, false )
	o.load_media
	menus << o
end
menu_num = menus.size
page_max = menu_num / page_limit + 1


puts "Paging poarts<br>" if @debug
page_start = 1
page_end = page_max
if page_end > 5
	if page > 3
		page_start = page - 3
		page_start = page_max - 6 if page_max - page_start < 7
	end
	if page_end - page < 3
		page_end = page_max
	else
		page_end = page + 3
		page_end = 7 if page_end < 7
	end
else
	page_end = page_max
end
html_paging = pageing_html( page, page_start, page_end, page_max, l )


puts "Menu range<br>" if @debug
menu_start = page_limit * ( page - 1 )
menu_end = menu_start + page_limit - 1
menu_end = r.size if menu_end >= r.size
if @debug
	puts "page_start: #{page_start}<br>"
	puts "page_end: #{page_end}<br>"
	puts "page_max: #{page_max}<br>"
	puts "menu_start: #{menu_start}<br>"
	puts "menu_end: #{menu_end}<br>"
	puts "<hr>"
end


menu_html = ''
menu_count = 0
menus.each do |e|
	if menu_count >= menu_start && menu_count <= menu_end
		menu_html << '<tr style="font-size:medium;">'

		if e.media[0] != nil
			menu_html << "<td><img src='#{$PHOTO}/#{e.media[0]}-tns.jpg'></a></td>"
		else
			menu_html << "<td>-</td>"
		end

		menu_html << "<td onclick=\"initMT( 'load', '#{e.code}' )\">#{e.name}</td>"

		menu_html << "<td>"
		menu_html << l[:globe] if e.public == 1
		menu_html << l[:lock] if e.protect == 1
		menu_html << "</td>"

		menu_html << "<td>#{e.label}</td>"
		menu_html << "<td>-</td>"

		menu_html << "<td>"
		if user.status >= 2
			menu_html << "<span onclick=\"addKoyomi( '#{e.code}', 1 )\">#{l[:calendar]}</span>&nbsp;&nbsp;"
		end
		menu_html << "</td>"

		menu_html << "<td>"
		if e.user == user.name
			menu_html << "<input type='checkbox' id='#{e.code}'>&nbsp;<span onclick=\"menuDelete( '#{e.code}', '#{e.name}' )\">#{l[:trash]}</span>" if e.protect != 1
		else
			menu_html << "<span onclick=\"menuImport( '#{e.code}' )\">#{l[:download]}</span>"
		end
		menu_html << "</td>"

	end
	menu_count += 1
end


html = <<-"HTML"
<div class='container-fluid'>
	<div class='row'>
		<div class='col-7'><h5>#{l[:menul]} (#{menu_num})</h5></div>
		<div class='col-5'>#{html_paging}</div>
	</div>
	<br>

	<div class='row'>
		<div class='col-3'>
			<div class="input-group input-group-sm">
				<label class="input-group-text" for="range">#{l[:range]}</label>
				#{html_range}
			</div>
		</div>
		<div class='col-4'>
			<div class="input-group input-group-sm">
				<label class="input-group-text #{school_flavor}" id='label_groupl' onclick="switchLabelsetl( '#{normal_label_c}', '#{school_label_c}' )">#{l[:label]}</label>
				#{html_label}
			</div>
		</div>
	</div>
	<br>

	<div class='row'>
		<div class='col-11'>
			<div class='row'><button class="btn btn-info btn-sm" type="button" onclick="changeMenuPage( '#{page}' )">#{l[:limit]}</button></div>
		</div>
		<div class='col-1'>
			<div class='row'><button class="btn btn-warning btn-sm" type="button" onclick="recipeList( 'reset' )">#{l[:reset]}</button></div>
		</div>
	</div>
	<br>

	<table class="table table-sm table-hover">
	<thead>
		<tr>
			<td>#{l[:photo]}</td>
			<td>#{l[:menu_name]}</td>
			<td>#{l[:status]}</td>
			<td>#{l[:label]}</td>
			<td>#{l[:extend_num]}</td>
			<td>#{l[:operation]}</td>
			<td></td>
		</tr>
	</thead>
	#{menu_html}
	</table>

	<div class='row'>
		<div class='col-7'></div>
		<div class='col-5'>#{html_paging}</div>
	</div>
HTML

puts html

#==============================================================================
# POST PROCESS
#==============================================================================
puts 'Saving menul config<br>' if @debug
menul = "#{page}:#{range}:#{label}"
db.query( "UPDATE #{$TB_CFG} SET menul='#{menul}' WHERE user='#{user.name}';", true )


#==============================================================================
# FRONT SCRIPT START
#==============================================================================
if command == 'init'
	js = <<-"JS"
<script type='text/javascript'>

var postReq = ( command, data, successCallback ) => {
	$.post( '#{myself}', { command, ...data })
		.done( successCallback )
		.fail(( jqXHR, textStatus, errorThrown ) => {
			console.error( "Request failed: ", textStatus, errorThrown );
			alert( "An error occurred. Please try again." );
		});
}

//
var changeMenuPage = (page) => {
	const range = $( "#range" ).val();
	const label = $( "#label_list" ).val();
	postReq( 'view', { page, range, label }, ( data ) => { $( "#L1" ).html( data );});
};


//
var menuDelete = ( code, menu_name ) => {
	if ( $( `#${code}` ).is( ":checked" )) {
		postReq( 'delete', { code }, ( data ) => {
			$( "#L1" ).html( data );
			displayVIDEO( menu_name );
		});
	} else {
		displayVIDEO( 'Check! (>_<)' );
	}
};


//
var menuImport = ( code ) => {
	$.post( 'import', { code }, ( data ) => {
		$( "#L1" ).html( data );
		displayVIDEO( code );
	});
};


// Changing label set
var switchLabelsetl = ( normal_label_c, school_label_c ) => {
	const label_status = $( '#normal_label_list0' ).css( 'display' );

	if ( school_label_c > 0 ) {
		if ( label_status === 'inline' ) {
			for ( let i = 0; i <= normal_label_c; i++ ) {
				$( `#normal_label_list${i}` ).hide();
			}
			for (let i = 1; i <= school_label_c; i++) {
				$( `#school_label_list${i}` ).css( 'display', 'inline' );
			}
			$( '#label_list' ).prop( 'selectedIndex', normal_label_c + 1 );
		} else {
			for ( let i = 0; i <= normal_label_c; i++ ) {
				$(`#normal_label_list${i}`).css('display', 'inline');
			}
			for ( let i = 1; i <= school_label_c; i++ ) {
				$( `#school_label_list${i}` ).hide();
			}
			$( '#label_list' ).prop( 'selectedIndex', 0 );
		}
	}
};


</script>

JS
	puts js
end

puts '(^q^)' if @debug
