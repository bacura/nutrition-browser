#! /usr/bin/ruby
#encoding: utf-8
#Nutrition browser 2020 memory list 0.0.0 (2025/03/10)

#==============================================================================
# STATIC
#==============================================================================
@debug = false
myself = File.basename( __FILE__ )
tmp = 'tmp_tmp'

#==============================================================================
# LIBRARY
#==============================================================================
require './soul'
require './brain'
require './body'

#==============================================================================
# DEFINITION
#==============================================================================

# Language pack
def language_pack( language )
	l = Hash.new

	#Japanese
	l['ja'] = {
		list:		"一覧",\
		category:	"カテゴリー",\
		user:		"ユーザー",\
		new_cate:	"新規カテゴリー",\
		regist:		"登録",\
		new_reg:	"新規ポインタ登録",\
		key:		"ポインタ",\
		key_num:	"ポインタ数",\
		memory:		"記憶",\
		save:		"保存",\
		media:		"メディア",\
		memory_edit:"記憶管理:",\
		return:		"<img src='bootstrap-dist/icons/signpost-r.svg' style='height:2em; width:2em;'>",\
		delete:		"<img src='bootstrap-dist/icons/trash.svg' style='height:1.2em; width:1.2em;'>"
	}

	return l[language]
end

#### init category list
def html_category_list( memory, l )
	html = ''

	if memory.user.status >= 8
		html << '<div class="row">'
		html << '<div class="col-7"></div>'
		html << '<div class="col-5">'
		html << '<div class="input-group input-group-sm">'
		html << "	<span class='input-group-text' id='inputGroup-sizing-sm'>#{l[:new_cate]}</span>"
		html << '	<input type="text" class="form-control" id="new_category">'
		html << "	<button type='button' class='btn btn-success' onclick=\"newCategory()\">#{l[:regist]}</button>"
		html << '</div></div>'
		html << '</div>'
		html << '<br>'
	end

	html << '<table class="table table-striped">'
	html << '<thead>'
	html << "<th>#{l[:category]}</th>"
	html << "<th>#{l[:key_num]}</th>"
	html << "<th></th>"
	html << '<th></th>'
	html << '</thead>'

	categories = memory.get_categories()
	categories.each.with_index do |e, i|
		pointer_num = memory.get_pointers( e ).size
		html << "<tr>"
		if memory.user.status >= 8
			html << "<td><input type='text' size='64' id='#{e}' value='#{e}' onchange=\"changeCategory( '#{e}' )\"></td>"
			html << "<td>#{pointer_num}</td>"
			html << "<td><button type='button' class='btn btn-primary btn-sm' onclick=\"listPointers( '#{e}', 'front' )\">#{l[:list]}</button></td>"
			html << "<td><input type='checkbox' id='delete_check#{i}'>&nbsp;"
			html << "<span onclick=\"deleteCategory( '#{e}', 'delete_check#{i}' )\">#{l[:delete]}</span></td>"
		else
			html << "<td>#{e}</td>"
			html << "<td>#{pointer_num}</td>"
			html << "<td><button type='button' class='btn btn-primary btn-sm' onclick=\"listPointers( '#{e}', 'front' )\">#{l[:list]}</button></td>"
			html << "<td></td>"
		end
		html << "</tr>"
	end

	html << '</table>'

	return html
end

#==============================================================================
# Main
#==============================================================================
html_init( nil )

user = User.new( @cgi )
user.debug if @debug
l = language_pack( user.language )
db = Db.new( user, @debug, false )
memory = Memory.new( user )

puts 'Getting POST data<br>' if @debug
command = @cgi['command']
mode = @cgi['mode']
code = @cgi['code']
category = @cgi['category']
new_category = @cgi['new_category']
pointer = @cgi['pointer']
content = @cgi['content']
if @debug
	puts "command:#{command}<br>\n"
	puts "mode:#{mode}<br>\n"
	puts "code:#{code}<br>\n"
	puts "category:#{category}<br>\n"
	puts "new_category:#{new_category}<br>\n"
	puts "pointer:#{pointer}<br>\n"
	puts "content:#{content.size}<br>\n"
	puts "<hr>\n"
end


html_list = ''
case command
when 'init'
	html_list = html_category_list( memory, l )

when 'save'
	memory.load_cgi( @cgi )
	memory.code = generate_code( user.name, 'k' )
	memory.pointer = tmp
	memory.content = tmp
	memory.date = @datetime
	memory.save_db()

	html_list = html_category_list( memory, l )

when 'change'
	memory.load_cgi( @cgi )
	memory.change_category( new_category )

	html_list = html_category_list( memory, l )

when 'delete'
	memory.load_cgi( @cgi )
	memory.delete_category()

	html_list = html_category_list( memory, l )

when 'pointers'
	html_list = "<div class='row'>"
	html_list << "<div class='col' align='right'><button type='button' class='btn btn-success btn-sm nav_button' onclick=\"newMemory( '#{category}', '', 'front' )\">#{l[:new_reg]}</button></div>"
	html_list << "</div>"
	html_list << "<br>"

	html_list << "<table class='table table-sm table-striped'>"
	html_list << "<thead>"
	html_list << "<th>#{l[:key]}</th>"
	html_list << "<th>#{l[:memory]}</th>"
	html_list << "<th>#{l[:media]}</th>"
	html_list << "<th>#{l[:user]}</th>"
	html_list << "</thead>"

	memory.load_cgi( @cgi )

########### Temp
	range = 'user'
	range = '' if user.status >= 8
###########
	photo = Media.new( user )

	memory_solid = memory.get_solid( range )
	memory_solid.each do |e|
		unless e['content'] == tmp
			photo.origin = e['code']
			photo.base = 'memory'
			pp = photo.get_series().size

			e['content'] = '' if e['content'] == nil

			html_list << "<tr onclick=\"editMemory( '#{e['code']}', 'list' )\">"
			html_list << "<td>#{e['pointer']}</td>"

			if e['content'].size > 80
				html_list << "<td>#{e['content'][0, 80]}...</td>"
			else
				html_list << "<td>#{e['content']}</td>"
			end
			html_list << "<td>#{pp}</td>"
			html_list << "<td>#{e['user']}</td>"
			html_list << "</tr>"
		end
	end
	html_list << "</table>"
end


html_return = command == 'pointers'? "<div align='center' class='col joystic_koyomi' onclick=\"initMemoryList()\">#{l[:return]}</div>" : ''


puts 'HTML<br>' if @debug
html = <<-"HTML"
<div class='container-fluid'>
	<div class='row'>
		<div class='col'><h5>#{l[:memory_edit]} #{category}</h5></div>
		#{html_return}
	</div>
	<br>

	#{html_list}
</div>
HTML

puts html

#==============================================================================
# POST PROCESS
#==============================================================================


#==============================================================================
#FRONT SCRIPT
#==============================================================================
if command == 'init'
	js = <<-"JS"
<script type='text/javascript'>

var postReq_ml = ( command, data, successCallback ) => {
	$.post( '#{myself}', { command, ...data })
		.done( successCallback )
		.fail(( jqXHR, textStatus, errorThrown ) => {
			console.error( "Request failed: ", textStatus, errorThrown );
			alert( "An error occurred. Please try again." );
		}
	);
}

// Save New category
var newCategory = () => {
	const category = $( '#new_category' ).val();
	if( category != '' ){
		postReq_ml( 'save', { category }, data => { $( "#L1" ).html( data );});
	}else{
		displayVIDEO( 'Category name!(>_<)' );
	}
};

// Delete category
var deleteCategory = ( category, delete_check_no ) => {
	if( $( "#" + delete_check_no ).is( ":checked" )){
		postReq_ml( 'delete', { category }, data => { $( "#L1" ).html( data );});
	}else{
		displayVIDEO( 'Check!' );
	}
};

// Change category name
var changeCategory = ( category ) => {
	const new_category = $( '#' + category ).val();
	if( category != '' ){
		postReq_ml( 'change', { category, new_category }, data => { $( "#L1" ).html( data );});
	}else{
		displayVIDEO( 'Category name!(>_<)' );
	}
};

// List each pointer
var listPointers = ( category ) => {
	postReq_ml( 'pointers', { category }, data => { $( "#L1" ).html( data );});
};

</script>
JS

	puts js

end

puts '<br>(^q^)' if @debug
