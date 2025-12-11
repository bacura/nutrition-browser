#! /usr/bin/ruby
#encoding: utf-8
#Nutrition browser 2020 recipe editor 0.2.4 (2025/03/29)

#==============================================================================
#STATIC
#==============================================================================
@debug = false
myself = File.basename( __FILE__ )
#$UDIC = '/usr/local/share/mecab/dic/ipadic/sys.dic'

#==============================================================================
#COMMON LIBRARY
#==============================================================================
require './soul'
require './brain'
require './body'
require 'natto'

#==============================================================================
#DEFINITION
#==============================================================================
def language_pack( language )
	l = Hash.new
# Language pack


	#Japanese
	l['jp'] = {
		type: 		'料理スタイル',
		role: 		'献立区分',
		tech: 		'調理区分',
		time: 		'目安時間(分)',
		cost: 		'目安費用(円)',
		name: 		'レシピ名',
		save: 		'保存',
		protocol: 	'調理手順',
		special: 	'【行頭特殊記号】　<b>!</b>[文字]:強調、<b>@</b>[文字]:ただし書き（薄カッコ表示）、<b>#</b>[文字]:コメント（非表示）、<b>+</b>[レシピコード]:参照レシピ',
		root: 		'母',
		branch: 	'娘',
		favorite: 	'<img src="bootstrap-dist/icons/star-fill-y.svg" style="height:1.0em; width:1.0em;">お気に入り',
		draft: 		'<img src="bootstrap-dist/icons/cone-striped.svg" style="height:1.0em; width:1.0em;">仮組',
		public: 	'<img src="bootstrap-dist/icons/globe.svg" style="height:1.0em; width:1.0em;">公開',
		protect: 	'<img src="bootstrap-dist/icons/lock-fill.svg" style="height:1.0em; width:1.0em;">保護',
		camera: 	'<img src="bootstrap-dist/icons/camera.svg" style="height:1.2em; width:1.2em;">',
		link: 		'<img src="bootstrap-dist/icons/paperclip.svg" style="height:2.4em; width:2.4em;">',
		division: 	'<img src="bootstrap-dist/icons/virus-p.svg" style="height:1.2em; width:1.2em;">',
		mdm: 		'<img src="bootstrap-dist/icons/diagram-3.svg" style="height:2.4em; width:2.4em;">'
	}

	return l[language]
end


#==============================================================================
# Main
#==============================================================================
html_init( nil )

user = User.new( @cgi )
user.debug if @debug
l = language_pack( user.language )
db = Db.new( user, @debug, false )


#### POST
command = @cgi['command']
code = @cgi['code']
root = @cgi['root']
if @debug
	puts "commnad:#{command}<br>"
	puts "code:#{code}<br>"
	puts "root:#{code}<br>"
end

recipe = Recipe.new( user )
recipe.debug if @debug

case command
when 'protocol'
	recipe.load_db( code, true ) if code != ''
	recipe.protocol = @cgi['protocol']
	recipe.date = @datetime
	recipe.update_db
	exit

when 'save', 'division'
	recipe.load_cgi( @cgi )

	# Avoiding loop
	 recipe.root = '' if recipe.root == recipe.code

	# excepting for tags
	recipe.protocol = wash( recipe.protocol )

	r = db.query( "SELECT sum, name, dish from #{$MYSQL_TB_SUM} WHERE user='#{user.name}';", false )
	if r.first['name'] == ''
		puts 'Inserting new recipe<br>' if @debug
		recipe.code = generate_code( user.name, 'r' )
		recipe.sum = r.first['sum']
		recipe.dish = r.first['dish'].to_i
  		recipe.insert_db

	else
		puts 'Updating recipe<br>' if @debug
		pre_recipe = Recipe.new( user )
		pre_recipe.code = recipe.code
		pre_recipe.load_db( code, true )
		recipe.sum = r.first['sum']
		recipe.dish = r.first['dish'].to_i

		copy_flag = false
		original_user = nil

		if user.name != pre_recipe.user.name
			puts 'Import mode<br>' if @debug
			copy_flag = true
			original_user = pre_recipe.user.name
			recipe.favorite = 0
			recipe.draft = 1
			recipe.user = user
			recipe.sum = r.first['sum']
			recipe.dish = r.first['dish'].to_i
		end

		puts 'Canceling public mode of recipe using puseudo user foods<br>' if @debug
		a = recipe.sum.split( "\t" )
		a.each do |e|
			sum_items = e.split( ':' )
			recipe.public = 0 if /^U/ =~ sum_items[0]
		end

		if recipe.draft == 1
			puts 'Draft mode<br>' if @debug
			recipe.protect = 0
			recipe.public = 0

			recipe.update_db

			copy_flag = true if command == 'division'

		elsif recipe.draft == 0 && recipe.protect == 0
			puts 'Normal mode<br>' if @debug
			if recipe.name == pre_recipe.name
				recipe.update_db
			else
				recipe.protect = 1 if recipe.public == 1
				copy_flag = true
			end

		else
			puts 'Protect mode<br>' if @debug
			recipe.protect = 1 if recipe.public == 1
			if pre_recipe.protect == 0 && recipe.name == pre_recipe.name
				recipe.update_db
			else
				copy_flag = true
			end
		end

		if copy_flag
			puts "Copying recipe<br>" if @debug
			recipe.code = generate_code( user.name, 'r' )

			# Copying name
			if recipe.name == pre_recipe.name && user.name == pre_recipe.user.name && command != 'division'
				t = pre_recipe.name.match( /\((\d+)\)$/ )
				sn = 1
				sn = t[1].to_i + 1 if t != nil
				pre_recipe.name.sub!( /\((\d+)\)$/, '' )
				recipe.name = "#{pre_recipe.name}(#{sn})"
			end

			puts "checking media<br>" if @debug
			media = Media.new( user )
			media.origin = code
			media.get_series()

			puts "Copying photo<br>" if @debug
			media.series.each do |e|
				new_media_code = generate_code( user.name, 'p' )

				FileUtils.cp( "#{$PHOTO_PATH}/#{e}-tns.jpg", "#{$PHOTO_PATH}/#{new_media_code}-tns.jpg" ) if File.exist?( "#{$PHOTO_PATH}/#{e['code']}-tns.jpg" )
				FileUtils.cp( "#{$PHOTO_PATH}/#{e}-tn.jpg", "#{$PHOTO_PATH}/#{new_media_code}-tn.jpg" ) if File.exist?( "#{$PHOTO_PATH}/#{e['code']}-tn.jpg" )
				FileUtils.cp( "#{$PHOTO_PATH}/#{e}.jpg", "#{$PHOTO_PATH}/#{new_media_code}.jpg" ) if File.exist?( "#{$PHOTO_PATH}/#{e['code']}.jpg" )

				puts "Inserting into DB<br>" if @debug
				new_media = Media.new( user )
				new_media.origin = recipe.code
				new_media.code = new_media_code
				new_media.date = @datetime
				new_media.base = 'recipe'
				new_media.alt = recipe.name
				new_media.save_db()
			end

			recipe.insert_db
		end
	end

	db.query( "UPDATE #{$MYSQL_TB_SUM} SET name='#{recipe.name}', code='#{recipe.code}', protect='#{recipe.protect}' WHERE user='#{user.name}';", true )

when 'photo_upload'
	new_photo = Media.new( user )
	new_photo.load_cgi( @cgi )
	new_photo.save_photo( @cgi )
    new_photo.get_series()
    new_photo.save_db()

	code = @cgi['origin']
	recipe.load_db( code, true )

when 'photo_mv'
	target_photo = Media.new( user )
	target_photo.load_cgi( @cgi )
    target_photo.get_series()
    target_photo.move_series()
 
	code = @cgi['origin']
	recipe.load_db( code, true )

when 'photo_del'
	target_photo = Media.new( user )
	target_photo.load_cgi( @cgi )
	target_photo.delete_photo( true )
	target_photo.delete_db( true )

	code = @cgi['origin']
	recipe.load_db( code, true )
else
	# Loading recipe from DB
	recipe.load_db( code, true ) if code != ''
end


puts "HTML SELECT Recipe attribute<br>" if @debug
check_favorite = $CHECK[recipe.favorite]
check_public = $CHECK[recipe.public]
check_protect = $CHECK[recipe.protect]
check_draft =  $CHECK[recipe.draft]
file_disabled = false
if user.name != recipe.user.name
	check_favorite = 'DISABLED'
	check_public = 'DISABLED'
	check_protect = 'DISABLED'
	check_draft = 'CHECKED DISABLED'
	file_disabled = true
end


puts "HTML SELECT Recipe type<br>" if @debug
html_type = l[:type]
html_type << '<select class="form-select form-select-sm" id="type">'
@recipe_type.size.times do |i| html_type << "<option value='#{i}' #{$SELECT[i == recipe.type]}>#{@recipe_type[i]}</option>" end
html_type << '</select>'


puts "HTML SELECT Recipe role<br>" if @debug
html_role = l[:role]
html_role << '<select class="form-select form-select-sm" id="role">'
@recipe_role.size.times do |i| html_role << "<option value='#{i}' #{$SELECT[i == recipe.role]}>#{@recipe_role[i]}</option>" end
if recipe.role == 100
	html_role << "<option value='100' SELECTED>[ 調味％ ]</option>"
else
	html_role << "<option value='100'>[ 調味％ ]</option>"
end
html_role << '</select>'


puts "HTML SELECT Cooking technique<br>" if @debug
html_tech = l[:tech]
html_tech << '<select class="form-select form-select-sm" id="tech">'
@recipe_tech.size.times do |i| html_tech << "<option value='#{i}' #{$SELECT[i == recipe.tech]}>#{@recipe_tech[i]}</option>" end
html_tech << '</select>'


puts "HTML SELECT Cooking time<br>" if @debug
html_time = l[:time]
html_time << '<select class="form-select form-select-sm" id="time">'
@recipe_time.size.times do |i| html_time << "<option value='#{i}' #{$SELECT[i == recipe.time]}>#{@recipe_time[i]}</option>" end
html_time << '</select>'


puts "HTML SELECT Cooking cost<br>" if @debug
html_cost = l[:cost]
html_cost << '<select class="form-select form-select-sm" id="cost">'
@recipe_cost.size.times do |i| html_cost << "<option value='#{i}' #{$SELECT[i == recipe.cost]}>#{@recipe_cost[i]}</option>" end
html_cost << '</select>'


division = ''
division = "<span onclick=\"recipeSave( 'division', '#{recipe.code}' )\">#{l[:division]}</span>" if recipe.draft == 1


puts "branche parts<br>" if @debug
branche = "<div class='col' id='tree' style='display:none;'>"
r = db.query( "SELECT name, code FROM #{$MYSQL_TB_RECIPE} WHERE user='#{user.name}' AND root='#{recipe.code}';", false )
if r.first && recipe.code != nil
    branche	<< '<ul class="list-group">'
	r.each do |e|
		branche << "<li class='list-group-item list-group-item-action' onclick='initCB( \"load\", \"#{e['code']}\", \"#{user.name}\" )'>#{e['name']}&nbsp;(#{e['code']})</li>"
	end
    branche	<< '</ul>'
    branche	<< "<input type='hidden' class='form-control' id='root' value='' >"
else
	branche	<< '<div class="input-group input-group-sm">'
	root_recipe_id = ''
	root_recipe_name = ''
	root_button = "<button class='btn btn-sm btn-secondary' onclick='words2Root()'>#{l[:root]}</button>"

	if recipe.root != ""
		rr = db.query( "SELECT name FROM #{$MYSQL_TB_RECIPE} WHERE user='#{user.name}' AND root='#{recipe.root}';", false )
		if rr.first
			root_button = "<button class='btn btn-sm btn-info' onclick='initCB( \"load\", \"#{recipe.root}\", \"#{user.name}\" )'>#{l[:root]}</button>"
			root_recipe_id = recipe.root
			root_recipe_name = rr.first['name']
		end
	end

	branche << root_button
    branche	<< "<input type='text' class='form-control' id='root' value='#{root_recipe_id}' >"
    branche	<< "<input type='text' class='form-control' id='root_name' value='#{root_recipe_name}' DISABLED>"
    branche	<< "&nbsp;&nbsp;#{division}"
    branche	<< '</div>'
end
branche << '</div>'


puts "Photo series parts<br>" if @debug
photo = Media.new( user )
photo.origin = code
photo.base = 'recipe'
photo.get_series()


puts "HTML FORM recipe<br>" if @debug
html = <<-"HTML"
<div class='container-fluid'>
	<div class='row'>
  		<div class="col-5">
			<div class="input-group input-group-sm">
				<label class="input-group-text" for="recipe_name">#{l[:name]}</label>
      			<input type="text" class="form-control" id="recipe_name" value="#{recipe.name}" required>
    		</div>
    	</div>
		<div class="col-1">
    	</div>
		<div class="col">
			<div class="form-check form-check-inline">
  				<label class="form-check-label">
    				<input class="form-check-input" type="checkbox" id="favorite" #{check_favorite}> #{l[:favorite]}
  				</label>
			</div>
			<div class="form-check form-check-inline">
  				<label class="form-check-label">
    				<input class="form-check-input" type="checkbox" id="public" #{check_public} onchange="recipeBit_public()"> #{l[:public]}
  				</label>
			</div>
			<div class="form-check form-check-inline">
  				<label class="form-check-label">
    				<input class="form-check-input" type="checkbox" id="protect" #{check_protect} onchange="recipeBit_protect()"> #{l[:protect]}
  				</label>
			</div>
			<div class="form-check form-check-inline">
  				<label class="form-check-label">
    				<input class="form-check-input" type="checkbox" id="draft" #{check_draft} onchange="recipeBit_draft()"> #{l[:draft]}
  				</label>
			</div>
		</div>
		<div class="col-1">
			<button class="btn btn-sm btn-outline-primary" type="button" onclick="recipeSave( 'save', '#{recipe.code}' )">#{l[:save]}</button>
    	</div>
    </div>
    <br>
	<div class='row'>
		<div class='col'>#{html_type}</div>
		<div class='col'>#{html_role}</div>
		<div class='col'>#{html_tech}</div>
		<div class='col'>#{html_time}</div>
		<div class='col'>#{html_cost}</div>
	</div>
	<br>
	<div class='row'>
		<div class="col-2">#{l[:protocol]}</div>
		<div class="col-10" align='right'>#{l[:special]}</div>
	</div>
	<div class='row'>
		<textarea class="form-control" id="protocol" rows="10" onchange="recipeProtocol( '#{recipe.code}' )">#{recipe.protocol}</textarea>
	</div>
	<br>

	<div class='row'>
		<div class='col-4'>
			#{photo.html_form_generic( !( recipe.code == nil || file_disabled ))}
		</div>
		<div class='col-1'>
			<span onclick="words2Protocol()" >#{l[:link]}</span>
		</div>
		<div class='col-1'>
			<span onclick="openTree()" >#{l[:mdm]}</span>
		</div>
		#{branche}
	</div>

	<hr>
	#{photo.html_series( '-tn', 200, recipe.protect )}

	<div class='row'>
		<div align='right' class='col code'>#{recipe.code}</div>
	</div>

</div>
HTML

puts html

#==============================================================================
#POST PROCESS
#==============================================================================

if command == 'save'
	puts "Save fcz<br>" if @debug
	food_no, food_weight, total_weight = extract_sum( recipe.sum, recipe.dish, 0 )
	fct = FCT.new( user, @fct_item, @fct_name, @fct_unit, @fct_frct, 1, 1 )
	fct.load_palette( @palette_bit_all )
	fct.set_food( food_no, food_weight, false )
	fct.calc
	fct.digit
	fct.save_fcz( recipe.name, 'recipe', recipe.code )
end


if command == 'save'
	mecab = Natto::MeCab.new()

	puts "Makeing alias dictionary<br>" if @debug
	dic = Hash.new
	r = db.query( "SELECT org_name, alias FROM #{$MYSQL_TB_DIC};", @debug )
	r.each do |e| dic[e['alias']] = e['org_name'] end

	target = []

	puts "Marking recipe name<br>" if @debug
	r = db.query( "SELECT * FROM #{$MYSQL_TB_RECIPEI} WHERE code='#{recipe.code}' AND word='#{recipe.name}' AND user='#{user.name}';", false )
	db.query( "INSERT INTO #{$MYSQL_TB_RECIPEI}  SET public='#{recipe.public}', user='#{user.name}', code='#{recipe.code}', word='#{recipe.name}';", true ) unless r.first
	recipe.name.gsub!( '　', "\t" )
	recipe.name.gsub!( '・', "\t" )
	recipe.name.gsub!( '／', "\t" )
	recipe.name.gsub!( '(', "\t" )
	recipe.name.gsub!( ')', "\t" )
	recipe.name.gsub!( '（', "\t" )
	recipe.name.gsub!( '）', "\t" )
	recipe.name.gsub!( /\t+/, "\s" )
	target << recipe.name

	a = recipe.protocol.split( "\n" )

	puts "Marking tag line<br>" if @debug
	if a[0] != nil && /^\#.+/ =~ a[0]
		a[0].gsub!( '#', '' )
		if a[0] != ''
			a[0].gsub!( "　", "\s" )
			tags = a[0].split( "\s" )
			tags.each do |e|
				if e != ''
					target << e
					r = db.query( "SELECT * FROM #{$MYSQL_TB_RECIPEI} WHERE code='#{recipe.code}' AND word='#{e}' AND user='#{user.name}';", false )
					db.query( "INSERT INTO #{$MYSQL_TB_RECIPEI}  SET public='#{recipe.public}', user='#{user.name}', code='#{recipe.code}', word='#{e}';", true ) unless r.first
				end
			end
		end
	end

	puts "Marking comment line<br>" if @debug
	if a[1] != nil && /^\#.+/ =~ a[1]
		a[1].gsub!( '#', '' )
		target << a[1] if a[1] != ''
	end

	target.each do |e|
		true_word = e
		true_word = dic[e] if dic[e] != nil
		mecab.parse( true_word ) do |n|
			a = n.feature.force_encoding( 'utf-8' ).split( ',' )
		 	if a[0] == '名詞' && ( a[1] == '一般' || a[1] == '普通名詞' || a[1] == '固有名詞' || a[1] == '人名' )
				r = db.query( "SELECT * FROM #{$MYSQL_TB_RECIPEI} WHERE user='#{user.name}' AND code='#{recipe.code}' AND word='#{n.surface}';", false )
				db.query( "INSERT INTO #{$MYSQL_TB_RECIPEI}  SET public='#{recipe.public}', user='#{user.name}', code='#{recipe.code}', word='#{n.surface}';", true ) unless r.first
		 	end
		end
	end

	puts "Marking SUM<br>" if @debug
	a = recipe.sum.split( "\t" )
	sum_code = []
	target_food = []
	a.each do |e| sum_code << e.split( ':' ).first end
	sum_code.each do |e|
		r = db.query( "SELECT name FROM #{$MYSQL_TB_TAG} WHERE FN='#{e}';", false )
		target_food << r.first['name'] if r.first
	end

	target_food.each do |e|
		r = db.query( "SELECT * FROM #{$MYSQL_TB_RECIPEI} WHERE user='#{user.name}' AND code='#{recipe.code}' AND word='#{e}';", false )
		db.query( "INSERT INTO #{$MYSQL_TB_RECIPEI}  SET public='#{recipe.public}', user='#{user.name}', code='#{recipe.code}', word='#{e}';", true ) unless r.first
	end
end


#==============================================================================
#FRONT SCRIPT
#==============================================================================
if command == 'init' || command == 'save'
	js = <<-"JS"
<script type='text/javascript'>

var postReq_recipe = ( command, data, successCallback ) => {
	$.post( '#{myself}', { command, ...data })
		.done( successCallback )
		.fail(( jqXHR, textStatus, errorThrown ) => {
			console.error( "Request failed: ", textStatus, errorThrown );
			alert( "An error occurred. Please try again." );
		});
};

// Recipe save
var recipeSave = ( com, code ) => {
	const recipe_name = $( "#recipe_name" ).val();
	if( !recipe_name ) {
		displayVIDEO( 'Recipe name! (>_<)' );
		return;
	}

	const type = $( "#type" ).val();
	const role = $( "#role" ).val();
	const tech = $( "#tech" ).val();
	const time = $( "#time" ).val();
	const cost = $( "#cost" ).val();
	const protocol = $( "#protocol" ).val();

	const favorite = $( "#favorite" ).is( ":checked" ) ? 1 : 0;
	const public = $( "#public" ).is( ":checked" ) ? 1 : 0;
	const protect = $( "#protect" ).is( ":checked" ) ? 1 : 0;
	const draft = $( "#draft" ).is( ":checked" ) ? 1 : 0;

	const root = $( "#root" ).length ? $( "#root" ).val() : '';
	postReq_recipe( com, { code, recipe_name, type, role, tech, time, cost, protocol, root, favorite, public, protect, draft }, data => {
		$( "#L2" ).html( data );
		initCB( 'reload', '' );
//		$.post( "photo.cgi", { command:'view_series', code:'', base:'recipe' }, function( data ){ $( "#LM" ).html( data );});
		displayVIDEO( recipe_name );
	});

}


// Recipe protocol moving save
var recipeProtocol = ( code ) => {
	const protect = $( "#protect" ).is( ":checked" ) ? 1 : 0;

	if (code !== '' && protect !== 1) {
		const protocol = $( "#protocol" ).val();

		postReq_recipe( 'protocol', { code, protocol }, () => {
			displayREC();
		});
	}
}


// Public button
var recipeBit_public = () => {
	if ( $( "#public" ).is( ":checked" ) ) {
		$( "#protect" ).prop( "checked", true );
		$( "#draft" ).prop( "checked", false );
	}
}

// Protect button
var recipeBit_protect = () => {
	if ( $( "#protect" ).is( ":checked" ) ) {
		$( "#draft" ).prop( "checked", false );
	} else {
		$( "#public" ).prop( "checked", false );
	}
}

// Draft button
var recipeBit_draft = () => {
	if ( $( "#draft" ).is( ":checked" ) ) {
		$( "#protect" ).prop( "checked", false );
		$( "#public" ).prop( "checked", false );
	}
}

// Tree button
var openTree = () => {
	const $tree = $( "#tree" );
	$tree.css( "display", $tree.css( "display" ) === "none" ? "block" : "none" );
}

// words paste to protocol button
var words2Protocol = () => {
	const $protocol = $( "#protocol" );
	const words = $( "#words" ).val();
	const cursorPos = $protocol[0].selectionStart;
	const protocolValue = $protocol.val();

	$protocol.val(
		protocolValue.substring( 0, cursorPos ) + words + protocolValue.substring( cursorPos )
	);
}

// words paste to mother button
var words2Root = () => {
	$( "#root" ).val( $( "#words" ).val());
}

/////////////////////////////////////////////////////////////////////////////////////////////

var PhotoUpload = () => {
	const formData = new FormData( $( '#recipe_puf' )[0] );
	formData.append( 'command', 'photo_upload' );
	formData.append( 'origin', '#{recipe.code}' );
	formData.append( 'base', 'recipe' );
	formData.append( 'alt', '#{recipe.name}' );
	formData.append( 'secure', '0' );

	$.ajax( {
		url: "#{myself}",
		type: 'POST',
		processData: false,
		contentType: false,
		data: formData,
		dataType: 'html',
		success: ( data ) => $( '#L2' ).html( data )
	} );
}

var photoMove = ( code, zidx ) => {

	postReq_recipe( 'photo_mv', { origin:'#{recipe.code}', code, zidx, base:'recipe' }, data => {
		$( '#L2' ).html( data );
		displayVIDEO( code );
	});
}

var photoDel = ( code ) => {
	postReq_recipe( 'photo_del', { origin:'#{recipe.code}', code, base:'recipe' }, data => $( '#L2' ).html( data ));
}

</script>
JS
	puts js

end

puts '(^q^)' if @debug
