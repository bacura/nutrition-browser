#! /usr/bin/ruby
#encoding: utf-8
#Nutrition browser koyomi fix fct editer 0.4.1 (2025/12/27)

#==============================================================================
# STATIC
#==============================================================================
@debug = false
myself = File.basename( __FILE__ )

#==============================================================================
# LIBRARY
#==============================================================================
require '../soul'
require '../brain'
require '../body'


#==============================================================================
# LANGUAGE PACK
#==============================================================================
def language_pack( language )
	l = Hash.new

	#Japanese
	l['ja'] = {
		save: 		"保　存",\
		g100: 		"100 g相当",\
		food_n: 	"食品名",\
		food_g:		"食品群",\
		weight:		"重量(g)",\
		palette:	"パレット",\
		min:		"分間",\
		week:		"-- １週間以内 --",\
		month:		"-- １ヶ月以内 --",\
		month3:		"-- ３ヶ月以内 --",\
		volume:		"個数",\
		carry_on:	"時間継承",\
		reference:	"参照",\
		history:	"履歴",\
		signpost:	"<img src='bootstrap-dist/icons/signpost-r.svg' style='height:2em; width:2em;'>",\
		clock:		"<img src='bootstrap-dist/icons/clock.svg' style='height:1.5em; width:1.5em;'>"
	}

	return l[language]
end

#==============================================================================
# METHODS
#==============================================================================
def generate_block_html( fct_set, fct_item, fct_name, fct_unit, palette, fix_opt )
	html = '<table class="table-sm table-striped" width="100%">'
	fct_set.each do |e|
		po = fct_item.index( e )
		if palette.bit[po] == 1
			html << "<tr><td>#{fct_name[e]}</td><td align='right' width='20%'><input type='text' class='form-control form-control-sm' id='kf#{e}' value=\"#{fix_opt[e].to_f}\"></td><td>#{fct_unit[e]}</td></tr>"
		else
			html << "<input type='hidden' value='0.0' id='kf#{e}'>"
		end
	end
	html << '</table>'
end

#==============================================================================
# MAIN
#==============================================================================
html_init( nil )

user = User.new( @cgi )
user.debug if @debug
l = language_pack( user.language )
db = Db.new( user, @debug, false )
koyomi = Calendar.new( user, 0, 0, 0 )


puts 'POST<br>' if @debug
command = @cgi['command']
yyyy = @cgi['yyyy'].to_i
mm = @cgi['mm'].to_i
dd = @cgi['dd'].to_i
tdiv = @cgi['tdiv'].to_i
hh_mm = @cgi['hh_mm']
meal_time = @cgi['meal_time'].to_i
order = @cgi['order'].to_i
palette_ = @cgi['palette']
palette_ = @palette_default_name.first if palette_.to_s.empty?
modifyf = @cgi['modifyf'].to_i
carry_on = @cgi['carry_on']
carry_on = 1 if @cgi['carry_on'] == ''
carry_on = carry_on.to_i
fix_ref = @cgi['fix_ref'].to_i
fix_his_code = @cgi['fix_his_code'].to_s
food_name = @cgi['food_name']
food_number = @cgi['food_number'].to_i
food_number = 1 if food_number == 0
food_weight = @cgi['food_weight']
food_weight = 100 if food_weight == nil || food_weight == ''|| food_weight == '0'
food_weight = BigDecimal( food_weight )


puts 'Getting standard meal start & time<br>' if @debug
start_times = []
meal_tiems = []
res = db.query( "SELECT bio FROM #{$TB_CFG} WHERE user=?", false, [user.name] )&.first
unless res['bio'].to_s.empty?

	begin
		bio = JSON.parse( res['bio'] )
	rescue JSON::ParserError => e
		puts "J(x_x)pE: #{e.message}<br>"
		exit
	end     

	start_times = [bio['bst'], bio['lst'], bio['dst']]
	meal_tiems = [bio['bti'].to_i, bio['lti'].to_i, bio['dti'].to_i]
end
hh_mm = start_times[tdiv] if hh_mm == '' || hh_mm == nil
hh_mm = @time_now.strftime( "%H:%M" ) if hh_mm == '' || hh_mm == nil
meal_time = meal_tiems[tdiv] if meal_time == 0


puts 'Loading FCT items<br>' if @debug
fix_opt = Hash.new
if command == 'init'
	@fct_min_nr.each do |e| fix_opt[e] = nil end
end


puts 'Updating fcs & koyomi<br>' if @debug
calendar = Calendar.new( user, yyyy, mm, dd )
ymd = calendar.ymd
koyomi = Koyomi.new( user )
koyomi.load_db( ymd )


code = nil
if command == 'save'
	puts 'Calculating fct<br>' if @debug
	@fct_min_nr.each do |e|
		if @cgi[e].to_s == '' || @cgi[e] == '-'
			fix_opt[e] = 0.0
		else
			t = @cgi[e]
			t.tr!( "０-９", "0-9" ) if /[０-９]/ =~ t
  			t.gsub!(/[．、。，,]/, '.')
			fix_opt[e] = ( BigDecimal( t.to_s ) / 100 * food_weight * food_number ).round( @fct_frct[e] )
		end
	end

	puts 'stetting SQL set <br>' if @debug
	fix_set = ''
	@fct_min_nr.each do |e| fix_set << "#{e}='#{fix_opt[e]}'," end
	fix_set.chop!

	#### modify
	if  modifyf == 1
		puts '[Modify mode]' if @debug
		koyomi_ = koyomi.get_sub( ymd, tdiv, order )
		if koyomi_
			code = koyomi_.split( "~" )[0]
			db.query( "UPDATE #{$TB_FCZ} SET name=?, date=?, #{fix_set} WHERE user=? AND base='fix' AND code=?", true, [food_name, "#{yyyy}-#{mm}-#{dd}", user.name, code] )
		end
		modified_koyomi = "#{code}~100~99~#{hh_mm}~#{meal_time}"
		koyomi.modify_sub( ymd, tdiv, order, modified_koyomi )
		koyomi.save_db()

	else
		fix_code = ''
		if fix_ref == 1 || fix_his_code != ''
			puts '[Ref mode]' if @debug
			fix_code = fix_his_code
		else
			puts '[Insert mode]' if @debug
 			fix_code = generate_code( user.name, 'z' )
			db.query( "INSERT INTO #{$TB_FCZ} SET base='fix', code=?, origin=?, date=?, name=?, user=?, #{fix_set};", true, [fix_code, "#{yyyy}-#{mm}-#{dd}-#{tdiv}", "#{yyyy}-#{mm}-#{dd}", food_name, user.name] )
		end
		new_koyomi = "#{fix_code}~100~99~#{hh_mm}~#{meal_time}"
		koyomi.add_sub( ymd, tdiv, new_koyomi )
		koyomi.save_db()
	end
end
if @debug
	puts "fix_opt: #{fix_opt}<br>\n"
	puts "<hr>\n"
end


#### modify
if command == 'modify' || modifyf == 1
	puts 'modify process<br>' if @debug
	koyomi_ = koyomi.get_sub( ymd, tdiv, order )
	if koyomi_
		elements = koyomi_.split( "~" )
		code = elements[0]
		hh_mm = elements[3]
		meal_time = elements[4].to_i
		res = db.query( "SELECT * FROM #{$TB_FCZ} WHERE user=? AND base='fix' AND code=?;", false, [user.name, code] )&.first
		if res
			food_name = res['name']
			@fct_min_nr.each do |e| fix_opt[e] = res[e].to_f end
		end
	end
	modifyf = 1
end


#### history
if command == 'history'
	puts 'HISTORY<br>' if @debug
	fix_his_code = @cgi['fix_his_code']
	res = db.query( "SELECT * FROM #{$TB_FCZ} WHERE user=? AND base='fix' AND code=?", false, [user.name, fix_his_code] )&.first
	if res
		food_name = res['name']
		@fct_min_nr.each do |e| fix_opt[e] = res[e].to_f end
	end
end


puts 'Setting palette<br>' if @debug
palette = Palette.new( user )
palette.set_bit( palette_ )
palette_html = ''
palette_html << "<div class='input-group input-group-sm'>"
palette_html << "<label class='input-group-text'>#{l[:palette]}</label>"
palette_html << "<select class='form-select form-select-sm' id='palette' onChange=\"selectKoyomiPalette( '#{yyyy}', '#{mm}', '#{dd}', '#{tdiv}', #{modifyf} )\">"
palette.sets.each_key do |k|
	palette_html << "<option value='#{k}' #{$SELECT[palette_ == k]}>#{k}</option>"
end
palette_html << "</select>"
palette_html << "</div>"


puts 'HTML FCT block<br>' if @debug
html_fct_blocks = []
html_fct_blocks[0] = generate_block_html( @fct_ew, @fct_item, @fct_name, @fct_unit, palette, fix_opt )
html_fct_blocks[1] = generate_block_html( @fct_pf, @fct_item, @fct_name, @fct_unit, palette, fix_opt )
html_fct_blocks[2] = generate_block_html( @fct_cho, @fct_item, @fct_name, @fct_unit, palette, fix_opt )
html_fct_blocks[3] = generate_block_html( @fct_m, @fct_item, @fct_name, @fct_unit, palette, fix_opt )
html_fct_blocks[4] = generate_block_html( @fct_fsv, @fct_item, @fct_name, @fct_unit, palette, fix_opt )

html_fct_blocks[5] = '<table class="table-sm table-striped" width="100%">'
@fct_wsv.each do |e|
	po = @fct_item.index( e )
	if palette.bit[po] == 1
		html_fct_blocks[5] << "<tr><td>#{@fct_name[e]}</td><td align='right' width='20%'><input type='text' class='form-control form-control-sm' id='kf#{e}' value='#{fix_opt[e].to_f}'></td><td>#{@fct_unit[e]}</td></tr>"
	else
		html_fct_blocks[5] << "<input type='hidden' value='0.0' id='kf#{e}'>"
	end
end
@fct_as.each do |e|
	po = @fct_item.index( e )
	if palette.bit[po] == 1
		html_fct_blocks[5] << "<tr><td>#{@fct_name[e]}</td><td align='right' width='20%'><input type='text' class='form-control form-control-sm' id='kf#{e}' value='#{fix_opt[e].to_f}'></td><td>#{@fct_unit[e]}</td></tr>"
	else
		html_fct_blocks[5] << "<input type='hidden' value='0.0' id='kf#{e}'>"
	end
end
html_fct_blocks[5] << '</table>'

puts 'SELECT HH block<br>' if @debug
meal_time_set = [5, 10, 15, 20, 30, 45, 60, 90, 120 ]
eat_time_html = "<div class='input-group input-group-sm'>"
eat_time_html << "<button class='btn btn-info' onclick=\"nowKoyomi( 'hh_mm_fix' )\">#{l[:clock]}</button>"
eat_time_html << "<input type='time' step='60' id='hh_mm_fix' value='#{hh_mm}' class='form-control' style='min-width:100px;'>"
eat_time_html << "<select id='meal_time_fix' class='form-select form-select-sm'>"
meal_time_set.each do |e|
	s = ''
	s = 'SELECTED' if meal_time == e
	eat_time_html << "	<option value='#{e}' #{s}>#{e}</option>"
end
eat_time_html << "</select>"
eat_time_html << "<label class='input-group-text'>#{l[:min]}</label>"
eat_time_html << "</div>"


#### carry_on_check
carry_on_disabled = ''
if command == 'modify'
	carry_on = 0
	carry_on_disabled = 'DISABLED'
end
carry_on_html = "<input class='form-check-input' type='checkbox' id='carry_on' #{$CHECK[carry_on]} #{carry_on_disabled}>"
carry_on_html << "<label class='form-check-label'>#{l[:carry_on]}</label>"


#### fix_his
fix_his_html = ''
his_today = @time_now.strftime( "%Y-%m-%d" )
his_w1 = ( @time_now - ( 60 * 60 * 24 * 7 )).strftime( "%Y-%m-%d" )
his_w1_ = ( @time_now - ( 60 * 60 * 24 * 8 )).strftime( "%Y-%m-%d" )
his_m1 = ( @time_now - ( 60 * 60 * 24 * 30 )).strftime( "%Y-%m-%d" )
his_m1_ = ( @time_now - ( 60 * 60 * 24 * 31 )).strftime( "%Y-%m-%d" )
his_m3 = ( @time_now - ( 60 * 60 * 24 * 90 )).strftime( "%Y-%m-%d" )

r = db.query( "SELECT code, name, origin FROM #{$TB_FCZ} WHERE user=? AND base='fix' AND date BETWEEN ? AND ? GROUP BY name;", false, [user.name, his_w1, his_today] )
rr = db.query( "SELECT code, name, origin FROM #{$TB_FCZ} WHERE user=? AND base='fix' AND date BETWEEN ? AND ? GROUP BY name;", false, [user.name, his_m1, his_w1_] )
rrr = db.query( "SELECT code, name, origin FROM #{$TB_FCZ} WHERE user=? AND base='fix' AND date BETWEEN ? AND ? GROUP BY name;", false, [user.name, his_m3, his_m1_] )
fix_his_html << "<div class='input-group input-group-sm'>"

fix_his_html << "<label class='input-group-text'>#{l[:history]}</label>"
fix_his_html << "<select class='form-select form-select-sm' id='fix_his_code' onchange=\"selectKoyomiHis( '#{yyyy}', '#{mm}', '#{dd}', '#{tdiv}' )\">"
fix_his_html << "<option value='' >#{l[:week]}</option>"
r.each do |e| fix_his_html << "<option value='#{e['code']}' #{$SELECT[e['code'] == fix_his_code]}>#{e['name']} (#{e['origin']})</option>" end
fix_his_html << "<option value='' >#{l[:month]}</option>"
rr.each do |e| fix_his_html << "<option value='#{e['code']}' #{$SELECT[e['code'] == fix_his_code]}>#{e['name']} (#{e['origin']})</option>" end
fix_his_html << "<option value='' >#{l[:month3]}</option>"
rrr.each do |e| fix_his_html << "<option value='#{e['code']}' #{$SELECT[e['code'] == fix_his_code]}>#{e['name']} (#{e['origin']})</option>" end
fix_his_html << '</select>'
fix_his_html << "</div>"

fix_ref_html = ''
fix_ref_html << '<div class="form-check form-switch">'
fix_ref_html << "<input class='form-check-input' type='checkbox' id='fix_ref' onChange=\"checkKyomiAsRef()\" #{$CHECK[command == 'history']} #{$DISABLE[command != 'history']}>"
fix_ref_html << "<label class='form-check-label' for='fix_ref'>#{l[:reference]}</label>"
fix_ref_html << '</div>'


puts 'HTML<br>' if @debug
html = <<-"HTML"
<div class='container-fluid'>
	<div class="row">
		<div class="col-4">
			#{fix_his_html}
		</div>
		<div class="col-1">
			#{fix_ref_html}
		</div>
		<div class="col-7">
			<div align='center' class='joystic_koyomi' onclick="returnFix2Edit()">#{l[:signpost]}</div>
		</div>
	</div>
	<br>
	<div class="row">
		<div class="col input-group input-group-sm">
			<label class='input-group-text'>#{l[:food_n]}</label>
			<input type="text" class="form-control form-control-sm" id="food_name" value="#{food_name}">
		</div>
		<div class="col">#{eat_time_html}</div>
		<div class="col">#{carry_on_html}</div>
	</div>
	<br>

	<div class="row">
		<div class="col">#{palette_html}</div>
		<div class="col"></div>
		<div class="col input-group input-group-sm">
			<div class="form-check">
				<input type="checkbox" class="form-check-input" id="g100_check" onChange="checkKyomiXOR100g()">
				<label class="form-check-label">#{l[:g100]}</label>
				</div>
				&nbsp;&nbsp;&nbsp;
			<label class="input-group-text">#{l[:weight]}</label>
			<input type="text" class="form-control form-control-sm" id="kffood_weight" placeholder="100" value="#{food_weight.to_f}" disabled>
		</div>
		<div class="col input-group input-group-sm">
			<label class="input-group-text">#{l[:volume]}</label>
			<input type="number" min='1' class="form-control form-control-sm" id="food_number" placeholder="1">
		</div>
	</div>
	<br>

	<div class="row">
		<div class="col-4">#{html_fct_blocks[0]}</div>
		<div class="col-4">#{html_fct_blocks[1]}</div>
		<div class="col-4">#{html_fct_blocks[2]}</div>
	</div>
	<hr>
	<div class="row">
		<div class="col-4">#{html_fct_blocks[3]}</div>
		<div class="col-4">#{html_fct_blocks[4]}</div>
		<div class="col-4">#{html_fct_blocks[5]}</div>
	</div>
	<br>

	<div class="row">
		<button class='btn btn-success btn-sm' type='button' onclick="saveKoyomiFix( '#{yyyy}', '#{mm}', '#{dd}', '#{tdiv}', '#{modifyf}', '#{order}' )">#{l[:save]}</button>
	</div>

</div>
HTML

puts html

#==============================================================================
#FRONT SCRIPT
#==============================================================================
if command == 'init' || command == 'modify'
	js = <<-"JS"
<script type='text/javascript'>

var postReq_kf = ( command, data, successCallback ) => {
	$.post( kp + '#{myself}', { command, ...data })
		.done( successCallback )
		.fail(( jqXHR, textStatus, errorThrown ) => {
			console.error( "Request failed: ", textStatus, errorThrown );
			alert( "An error occurred. Please try again." );
		});
}

// Koyomi fix save
var saveKoyomiFix = ( yyyy, mm, dd, tdiv, modifyf, order ) => {
	const food_name = $( "#food_name" ).val();
	const hh_mm = $( "#hh_mm_fix" ).val();
	const meal_time = $( "#meal_time_fix" ).val();
	const food_number = $( "#food_number" ).val();
	const fix_his_code = $( "#fix_his_code" ).val();
	let carry_on = 0;
	if( $( "#carry_on" ).is( ":checked" )){ carry_on = 1; }
	let fix_ref = 0;
	if( $( "#fix_ref" ).is( ":checked" )){ fix_ref = 1; }

	if( food_name != '' ){
		let food_weight = 100;
		if( $( "#g100_check" ).is( ":checked" )){ food_weight = $( "#kffood_weight" ).val(); }
		const ENERC = $( "#kfENERC" ).val();
		const ENERC_KCAL = $( "#kfENERC_KCAL" ).val();
		const WATER = $( "#kfWATER" ).val();

		const PROTCAA = $( "#kfPROTCAA" ).val();
		const PROT = $( "#kfPROT" ).val();
		const PROTV = $( "#kfPROTV" ).val();
		const FATNLEA = $( "#kfFATNLEA" ).val();
		const CHOLE = $( "#kfCHOLE" ).val();
		const FAT = $( "#kfFAT" ).val();
		const FATV = $( "#kfFATV" ).val();
		const CHOAVLM = $( "#kfCHOAVLM" ).val();
		const CHOAVL = $( "#kfCHOAVL" ).val();
		const CHOAVLDF = $( "#kfCHOAVLDF" ).val();
		const CHOV = $( "#kfCHOV" ).val();
		const FIB = $( "#kfFIB" ).val();
		const POLYL = $( "#kfPOLYL" ).val();
		const CHOCDF = $( "#kfCHOCDF" ).val();
		const OA = $( "#kfOA" ).val();

		const ASH = $( "#kfASH" ).val();
		const NA = $( "#kfNA" ).val();
		const K = $( "#kfK" ).val();
		const CA = $( "#kfCA" ).val();
		const MG = $( "#kfMG" ).val();
		const P = $( "#kfP" ).val();
		const FE = $( "#kfFE" ).val();
		const ZN = $( "#kfZN" ).val();
		const CU = $( "#kfCU" ).val();
		const MN = $( "#kfMN" ).val();
		const ID = $( "#kfID" ).val();
		const SE = $( "#kfSE" ).val();
		const CR = $( "#kfCR" ).val();
		const MO = $( "#kfMO" ).val();

		const RETOL = $( "#kfRETOL" ).val();
		const CARTA = $( "#kfCARTA" ).val();
		const CARTB = $( "#kfCARTB" ).val();
		const CRYPXB = $( "#kfCRYPXB" ).val();
		const CARTBEQ = $( "#kfCARTBEQ" ).val();
		const VITA_RAE = $( "#kfVITA_RAE" ).val();
		const VITD = $( "#kfVITD" ).val();
		const TOCPHA = $( "#kfTOCPHA" ).val();
		const TOCPHB = $( "#kfTOCPHB" ).val();
		const TOCPHG = $( "#kfTOCPHG" ).val();
		const TOCPHD = $( "#kfTOCPHD" ).val();
		const VITK = $( "#kfVITK" ).val();

		const THIA = $( "#kfTHIA" ).val();
		const RIBF = $( "#kfRIBF" ).val();
		const NIA = $( "#kfNIA" ).val();
		const NE = $( "#kfNE" ).val();
		const VITB6A = $( "#kfVITB6A" ).val();
		const VITB12 = $( "#kfVITB12" ).val();
		const FOL = $( "#kfFOL" ).val();
		const PANTAC = $( "#kfPANTAC" ).val();
		const BIOT = $( "#kfBIOT" ).val();
		const VITC = $( "#kfVITC" ).val();

		const ALC = $( "#kfALC" ).val();
		const NACL_EQ = $( "#kfNACL_EQ" ).val();

		const FASAT = $( "#kfFASAT" ).val();
		const FAMS = $( "#kfFAMS" ).val();
		const FAPU = $( "#kfFAPU" ).val();
		const FAPUN3 = $( "#kfFAPUN3" ).val();
		const FAPUN6 = $( "#kfFAPUN6" ).val();

		const FIBTG = $( "#kfFIBTG" ).val();
		const FIBSOL = $( "#kfFIBSOL" ).val();
		const FIBINS = $( "#kfFIBINS" ).val();
		const FIBTDF = $( "#kfFIBTDF" ).val();
		const FIBSDFS = $( "#kfFIBSDFS" ).val();
		const FIBSDFP = $( "#kfFIBSDFP" ).val();
		const FIBIDF = $( "#kfFIBIDF" ).val();
		const STARES = $( "#kfSTARES" ).val();

		postReq_kf( 'save', {
			yyyy, mm, dd, tdiv, hh_mm, meal_time,
			food_name, food_weight, food_number, modifyf, fix_ref, fix_his_code, carry_on, order,
			ENERC, ENERC_KCAL, WATER,
			PROTCAA, PROT, PROTV, FATNLEA, CHOLE, FAT, FATV, CHOAVLM, CHOAVL, CHOAVLDF, CHOV, FIB, POLYL, CHOCDF, OA,
			ASH, NA, K, CA, MG, P, FE, ZN, CU, MN, ID, SE, CR, MO,
			RETOL, CARTA, CARTB, CRYPXB, CARTBEQ, VITA_RAE, VITD, TOCPHA, TOCPHB, TOCPHG, TOCPHD, VITK,
			THIA, RIBF, NIA, NE, VITB6A, VITB12, FOL, PANTAC, BIOT, VITC,
			ALC, NACL_EQ,
			FASAT, FAMS, FAPU, FAPUN3, FAPUN6,
			FIBTG, FIBSOL, FIBINS, FIBTDF, FIBSDFS, FIBSDFP, FIBIDF, STARES
		}, data => {
			$( "#L3" ).html( data );

			$.post( kp + "koyomi-edit.cgi", { yyyy, mm, dd }, function( data ){
				$( "#L2" ).html( data );

				dl2 = true;
				dl3 = false;
				displayBW();
				displayREC();
			});

		});
	} else{
		displayVIDEO( 'Food name! (>_<)' );
	}
};


var selectKoyomiPalette = ( yyyy, mm, dd, tdiv, modifyf ) => {
	displayVIDEO( modifyf );
	const palette = $( "#palette" ).val();
	postReq_kf( 'palette', { yyyy, mm, dd, tdiv, palette, modifyf }, data => { $( "#L3" ).html( data );});
};


var selectKoyomiHis = ( yyyy, mm, dd, tdiv ) => {
	const fix_his_code = $( "#fix_his_code" ).val();
	if( fix_his_code != '' ){
		postReq_kf( "history", { yyyy, mm, dd, tdiv, fix_his_code }, data => { $( "#L3" ).html( data );});
	}
};


var checkKyomiAsRef = () => {
	if( $( "#fix_ref" ).is( ":checked" )){
		$( "#kffood_weight" ).prop( "disabled", false );
	}else{
		$( "#kffood_weight" ).prop( "disabled", true );
	}
};


var checkKyomiXOR100g = () => {
	if( $( "#g100_check" ).is( ":checked" )){
		$( "#kffood_weight" ).prop( "disabled", false );
	}else{
		$( "#kffood_weight" ).prop( "disabled", true );
	}
};

var returnFix2Edit = () => {
	dl2 = true;
	dl3 = false;
	displayBW();
};

</script>
JS

	puts js
end

puts '<br>(^q^)' if @debug
