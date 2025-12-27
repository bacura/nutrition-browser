#! /usr/bin/ruby
#encoding: utf-8
#Nutrition browser print page selector 0.0.6 (2024/06/07)

#==============================================================================
#STATIC
#==============================================================================
@debug = false
#script = File.basename( $0, '.cgi' )

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
		'non' 		=> "指定のレシピは存在しません。",\
		'palette'	=> "パレット",\
		'precision'	=> "精密合計",\
		'ew'		=> "予想g",\
		'fract'		=> "端数",\
		'round'		=> "四捨五入",\
		'ceil'		=> "切り上げ",\
		'floor'		=> "切り捨て",\
		'hr'		=> "高解像度画像",\
		'basic'		=> "基本レシピ",\
		'ditail'	=> "詳細レシピ",\
		'eiyo'		=> "栄養レシピ",\
		'full'		=> "フルレシピ",\
		'cb-plus'	=> "<img src='bootstrap-dist/icons/clipboard-plus.svg' style='height:2em; width:2em;'>",\
		'return'	=> "<img src='bootstrap-dist/icons/signpost-r.svg' style='height:2em; width:2em;'>"
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


puts 'Getting POST<br>' if @debug
command = @cgi['command']
code = @cgi['code']
if @debug
	puts "command: #{command}<br>"
	puts "code: #{code}<br>"
	puts "<hr>"
end


puts 'Checking recipe code<br>' if @debug
r = db.query( "SELECT * FROM #{$TB_RECIPE} WHERE code='#{code}';", false )
unless r.first
	puts "#{l['non']}(#{code})"
	exit( 9 )
end
recipe_name = r.first['name']
recipe_dish = r.first['dish']


puts 'Generating palette HTML<br>' if @debug
palette_html = ''
#### Setting palette
palette_name = []
r = db.query( "SELECT * from #{$TB_PALETTE} WHERE user='#{user.name}';", false )
r.each do |e| palette_name << e['name'] end
palette_name.size.times do |c| palette_html << "<option value='#{palette_name[c]}'>#{palette_name[c]}</option>" end


puts 'Cooking school HTML<br>' if @debug
csc = ''
cs_disabled = ''
if user.status == 5 ||  user.status >= 8
	r = db.query( "SELECT enable FROM #{$TB_SCHOOLC} WHERE user='#{user.name}';", false )
	if r.first
		enable = r.first['enable']
		cs_disabled = 'DISABLED' if enable != 1
	else
		cs_disabled = 'DISABLED'
	end
else
	cs_disabled = 'DISABLED'
end

puts 'HTML<br>' if @debug
html = <<-"HTML"
<div class='container-fluid'>
	<div class='row'>
		<div class='col-6'><h4>#{recipe_name}</h4></div>
		<div align="center" class='col-6 joystic_koyomi' onclick="print_templateReturen()">#{l['return']}</div>
	</div>
	<br>

	<div class='row'>
		<div class='col-3'>
			<div class="input-group input-group-sm">
				<label class="input-group-text" for="palette">#{l['palette']}</label>
				<select class="form-select" id="palette">
					#{palette_html}
				</select>
			</div>
		</div>
		<div class='col-3' align='center'>
			<div class="form-check form-check-inline">
    			<input class="form-check-input" type="checkbox" id="frct_accu">#{l['precision']}
			</div>
			<div class="form-check form-check-inline">
    			<input class="form-check-input" type="checkbox" id="ew_mode">#{l['ew']}
			</div>
		</div>
		<div class='col-2'>
			<div class="input-group input-group-sm">
				<label class="input-group-text" for="frct_mode">#{l['fract']}</label>
				<select class="form-select" id="frct_mode">
					<option value="1">#{l['round']}</option>
					<option value="2">#{l['ceil']}</option>
					<option value="3">#{l['floor']}</option>
				</select>
			</div>
		</div>
		<div class='col-1'></div>
<!--
		<div class='col-2'>
			<div class="form-check form-switch">
  				<input class="form-check-input" type="checkbox" id="csc" value='#{csc}' #{cs_disabled}>
  				<label class="form-check-label">#{l['']} (#{csc})</label>
			</div>
		</div>
-->
	</div>
	<br>

	<div class='row'>
		<div class='col print_card'>
			<div class="card" style="width: 14rem;" onclick="openPrint( '#{user.name}', '#{code}', '0', '#{recipe_dish}' )">
  				<img class="card-img-top" src="photo_/pvt_sample_2.png" alt="Card image cap">
  				<div class="card-body">
    				<h6 class="card-title">#{l['basic']}</h6>
  				</div>
			</div>
		</div>
		<div class='col print_card'>
			<div class="card" style="width: 14rem;" onclick="openPrint( '#{user.name}', '#{code}', '1', '#{recipe_dish}' )">
  				<img class="card-img-top" src="photo_/pvt_sample_4.png" alt="Card image cap">
  				<div class="card-body">
    				<h6 class="card-title">#{l['detail']}</h6>
  				</div>
			</div>
		</div>
		<div class='col print_card'>
			<div class="card" style="width: 14rem;" onclick="openPrint( '#{user.name}', '#{code}', '2', '#{recipe_dish}' )">
  				<img class="card-img-top" src="photo_/pvt_sample_6.png" alt="Card image cap">
  				<div class="card-body">
    				<h6 class="card-title">#{l['eiyo']}</h6>
  				</div>
			</div>
		</div>
		<div class='col print_card'>
			<div class="card" style="width: 14rem;" onclick="openPrint( '#{user.name}', '#{code}', '3', '#{recipe_dish}' )">
  				<img class="card-img-top" src="photo_/pvt_sample_8.png" alt="Card image cap">
  				<div class="card-body">
    				<h6 class="card-title">#{l['full']}</h6>
  				</div>
			</div>
		</div>
	</div>

	<hr>
	<div align="center"><button class='btn btn-sm' id="cp2cb">#{l['cb-plus']}</button><span id="recipe_print_url">#{$MYURL}printv.cgi?c=#{code}&t=1</span></div>
</div>

HTML

puts html

#==============================================================================
# FRONT SCRIPT START
#==============================================================================
if command == 'init'
	js = <<-"JS"
<script type='text/javascript'>

// Return to recipe list
var print_templateReturen = function(){
	flashBW();
	dl1 = true;
	displayBW();
};

// Open a recipe print screen
var openPrint = function( uname, code, template, dish ){
	const palette = document.getElementById( "palette" ).value;
	const frct_mode = document.getElementById( "frct_mode" ).value;
	if( document.getElementById( "frct_accu" ).checked ){ var frct_accu = 1; }else{ var frct_accu = 0; }
	if( document.getElementById( "ew_mode" ).checked ){ var ew_mode = 1; }else{ var ew_mode = 0; }

//	if( document.getElementById( "csc" ).checked ){
//		const csc = document.getElementById( "csc" ).value;
//		const url = 'printv.cgi?&c=' + code + '&t=' + template + '&d=' + dish + '&p=' + palette + '&fa=' + frct_accu + '&ew=' + ew_mode + '&fm=' + frct_mode + '&cs=' + csc;
//	}else{
		const url = 'printv.cgi?&c=' + code + '&t=' + template + '&d=' + dish + '&p=' + palette + '&fa=' + frct_accu + '&ew=' + ew_mode + '&fm=' + frct_mode;
//	}
	window.open( url, 'print' );
	displayVIDEO( 'Print page on the another tab' );
};

// Copy recipe print screen URL to the clip board
cp2cb.addEventListener( 'click', () => {
	if ( !navigator.clipboard ){
		displayVIDEO( 'Not available for cp2cp' );
		return;
	}

	navigator.clipboard.writeText( recipe_print_url.textContent ).then(
    	() => {
    		displayREC();
    	}
	);
});

</script>

JS

	puts js
end
