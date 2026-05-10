#! /usr/bin/ruby
#encoding: utf-8
#Nutrition browser Detective input 0.3.0 (2026/03/14)

#==============================================================================
#STATIC
#==============================================================================
@debug = false
myself = File.basename( __FILE__ )
@mod_path = 'detective_'
@result_limit = 10

#==============================================================================
#LIBRARY
#==============================================================================
require './soul'
require './brain'
require './body'

#==============================================================================
#DEFINITION
#==============================================================================

def language_pack( language )
	l = Hash.new

	#Japanese
	l['ja'] = {
		energy:			"エネルギー(kcal)",
		protein:		"たんぱく質(g)",
		fat:				"脂質(g)",
		carb:    		"炭水化物(g)",
		salt:     	"食塩相当量(g)",
		weight:   	"重量(g)",
		food_name:	"食品名",
		total:    	"合計",
		target:   	"目標量",
		ratio:    	"充足率",
		juten:			"重点",
		mode:				"モード",
		results:		"以前の結果",
		load:				"呼び出し",
		adapt:    	"<img src='bootstrap-dist/icons/hand-thumbs-up.svg' style='height:1.6em; width:1.6em;'>　採　用",
		suiri:    	"<img src='bootstrap-dist/icons/incognito.svg' style='height:1.6em; width:1.6em;'>　推　理"
	}

	return l[language]
end


#### MOD
def mod_list( user )
	mods = Dir.glob( "#{$HTDOCS_PATH}/#{@mod_path}/mod_*" )
	mods.map! do |x|
		x = File.basename( x )
		x = x.sub( 'mod_', '' )
		x = x.sub( '.rb', '' )
	end

	mod_list = Hash.new
	mods.each do |e|
		require "#{$HTDOCS_PATH}/#{@mod_path}/mod_#{e}.rb"
    mod = Object.const_get( "DetectiveMod_#{e}" )
    mod_list[e] = mod.lp( user.language )[:mod_name]
	end

	return mod_list
end


#### REC
def result_list( dbr, mod_list )
	result_list = Hash.new
	res = dbr.query( "SELECT * FROM results WHERE user=? AND base='detective' ORDER BY date DESC", false, [dbr.user.name] )
	res.each do |e|
  	next unless e['token']
  	cfg_base_json, = e['result'].split( '::' )
  	mode = JSON.parse( cfg_base_json )['mode'] rescue next
  	datetime = e['date'].strftime( "%Y-%m-%d %H:%M:%S" )
  	result_list[e['token']] = "[#{datetime}] #{mod_list[mode]}"
  end

	return result_list
end

def html_form_hints( cgi, db, dbr, l, cfg, mod_list )
	reasoning_button = ''
	res = db.query( "SELECT sum FROM #{$TB_SUM} WHERE user=?", false, [db.user.name] )&.first
	if res
		sum = res['sum']
		foods = sum.split( "\t" )
		reasoning_button = "<button type='button' class='btn btn-sm btn-warning' onclick=\"reasoning()\">#{l[:suiri]}</button>" if foods.size > 0
	end
	mode_option = ''
	mod_list.each do |k, v|
		mode_option << "<option value='#{k}' #{$SELECT[k == cgi['detective_mode']]}>#{v}</option>"
	end

	result_option = ''
	result_list = result_list( dbr, mod_list )
	result_list.each do |k, v|
		result_option << "<option value='#{k}' #{$SELECT[k == cgi['token']]}>#{v} </option>"
	end

html = <<-"HTML"
<div class='container-fluid'>
	<div class='row'>
		<div class='col-5'>
			<div class="input-group input-group-sm mb-3">
 				<span class="input-group-text">#{l[:mode]}</span>
				<select class="form-select form-select-sm" id="detective_mode">
					#{mode_option}
				</select>
			</div>
		</div>

		<div class='col-7'>
			<div class="input-group input-group-sm mb-3">
				<span class="input-group-text">#{l[:results]}</span>
				<select class="form-select form-select-sm" id="past_result">
					#{result_option}
				</select>
				<button type='button' class='btn btn-sm btn-outline-primary' onclick='loadResult()'>#{l[:load]}</button>
		</div>
		</div>
	</div>
	<br>

	<div class='row'>
		<div class='col-2'>
			#{l[:weight]}<br>
			<input type='text' id='weight' value='#{cfg.val['weight'].to_f.to_i}'>
		</div>
		<div class='col-2'>
			#{l[:energy]}<br>
			<input type='text' id='energy' value='#{cfg.val['energy'].to_f}'>
		</div>
		<div class='col-2'>
			#{l[:protein]}<br>
			<input type='text' id='protein' value='#{cfg.val['protein'].to_f}'>
		</div>
		<div class='col-2'>
			#{l[:fat]}<br>
			<input type='text' id='fat' value='#{cfg.val['fat'].to_f}'>
		</div>
		<div class='col-2'>
			#{l[:carb]}<br>
			<input type='text' id='carb' value='#{cfg.val['carb'].to_f}'>
		</div>
		<div class='col-2'>
			#{l[:salt]}<br>
			<input type='text' id='salt' value='#{cfg.val['salt'].to_f}'>
		</div>
	</div>
	<br>

	<div class='row'>
		#{reasoning_button}
	</div>
</div>
HTML

	return html
end


def html_table_result( db, l, weights, result, cfg )
	food_nos = []
	fw_ex = []
	weights.map! do |x| x.to_f end

	tbody = '<tbody>'
	result['details'].each.with_index do |food, i|
		res = db.query( "SELECT name FROM #{$TB_TAG} WHERE FN=?", false, [food['food_nos']] )&.first
		if res
			food_nos << food['food_nos']
			fw_ex << weights[i]
			tbody << '<tr>'
			tbody << "<td>#{res['name']}</td>"
			tbody << "<td>#{weights[i].round( 1 )}</td>"
			tbody << "<td>#{food['energy'].to_f.round( 1 )}</td>"
			tbody << "<td>#{food['protein'].to_f.round( 1 )}</td>"
			tbody << "<td>#{food['fat'].to_f.round( 1 )}</td>"
			tbody << "<td>#{food['carb'].to_f.round( 1 )}</td>"
			tbody << "<td>#{food['salt'].to_f.round( 1 )}</td>"
			tbody << '</tr>'
		end
	end

	fct_ex_total_ = ''
	result['total_nutrition'].each do |k, v| fct_ex_total_ << "<td>#{v.to_f.round( 1 )}</td>" end

	fct_ratio_ = ''
	result['fulfillment'].each do |k, v|
		percent = cfg.val[k] == 0 ? '-' : "#{v.to_f}%"
		fct_ratio_ << "<td class='text-danger'>#{percent}</td>"
	end

	fw_ex_solid = fw_ex.join( ':' )
	food_nos_solid = food_nos.join( ':' )

html = <<-"HTML"
<div class='container-fluid'>
	<div class='row'>
		<table class='table table-sm'>
			<thead>
				<tr>
					<td width='15%'class='cb_header'>#{l[:food_name]}</td>
					<td width='10%'class='cb_header'>#{l[:weight]}</td>
					<td width='10%'class='cb_header'>#{l[:energy]}</td>
					<td width='10%'class='cb_header'>#{l[:protein]}</td>
					<td width='10%'class='cb_header'>#{l[:fat]}</td>
					<td width='10%'class='cb_header'>#{l[:carb]}</td>
					<td width='10%' class='cb_header'>#{l[:salt]}</td>
				</td>
			<thead>

			<tbody>
			#{tbody}

			<tr class="table-secondary"><td colspan='7'></td></tr>

			<tr>
			<td>#{l[:total]}</td><td>#{weights.sum.round( 1 )}</td>
			#{fct_ex_total_}
			</tr>

			<tr>
			<td class='text-primary'>#{l[:target]}</td><td>#{cfg.val['weight'].to_i}</td>
			<td class='text-primary'>#{cfg.val['energy'].to_f}</td>
			<td class='text-primary'>#{cfg.val['protein'].to_f}</td>
			<td class='text-primary'>#{cfg.val['fat'].to_f}</td>
			<td class='text-primary'>#{cfg.val['carb'].to_f}</td>
			<td class='text-primary'>#{cfg.val['salt'].to_f}</td>
			</tr>

			<tr>
			<td>#{l[:ratio]}</td><td></td>
				#{fct_ratio_}
			</tr>

			</tbody>
		</table>
	</div>
	<br>
	<div class='row'>
		<button type='button' class='btn btn-sm btn-success' onclick="detectiveAdopt( '#{food_nos_solid}', '#{fw_ex_solid}' )">#{l[:adapt]}</button>
	</div>
</div>
HTML

	return html
end


def normalize_target( cfg )
  # 初期値を取得
  std_target = {
    weight:  BigDecimal( cfg.val['weight'].to_s ),
    energy:  BigDecimal( cfg.val['energy'].to_s ),
    protein: BigDecimal( cfg.val['protein'].to_s ),
    fat:     BigDecimal( cfg.val['fat'].to_s ),
    carb:    BigDecimal( cfg.val['carb'].to_s ),
    salt:    BigDecimal( cfg.val['salt'].to_s )
  }

  # 比率を計算（100g基準）
  std_ratio = 100.0 / std_target[:weight]
  
  # 100g基準に正規化
  std_target[:weight]  = 100
  std_target[:energy]  *= std_ratio
  std_target[:protein] *= std_ratio
  std_target[:fat]     *= std_ratio
  std_target[:carb]    *= std_ratio
  std_target[:salt]    *= std_ratio

  return std_target, std_ratio
end


# スケールバック関数（100g基準から元の重量に戻す）
def scale_back_weights( weights, cfg )
  scale = cfg.val['weight'] / 100.0  # 例: 105 / 100 = 1.05
  scaled_weights = weights.map do |w| w * scale end 
  
  # 合計が目標を超えないように再スケール
  total = scaled_weights.sum
  if total > cfg.val['weight']
    scale = cfg.val['weight'] / total
    scaled_weights = scaled_weights.map do |w| w * scale end
  end
  
  # 桁あわせ
  scaled_weights = scaled_weights.map do |w|
  	if w >= 10
  		w.to_i
  	else
  		w.round( 1 )
  	end
  end

  scaled_weights
end


def calculate_fulfillment( foods, weights, cfg )
  fulfillment = {}
  total_nutrition = { 'energy' => 0, 'protein' => 0, 'fat' => 0, 'carb' => 0, 'salt' => 0 }
  details = []

  weights.each_with_index do |w, i|
    food_nutrition = {
      'food_nos'	=> foods[i]['food_nos'],
      'weight'		=> w,
      'energy'		=> ( w * foods[i]['energy'] / 100.0 ),
      'protein'		=> ( w * foods[i]['protein'] / 100.0 ),
      'fat'				=> ( w * foods[i]['fat'] / 100.0 ),
      'carb'			=> ( w * foods[i]['carb'] / 100.0 ),
      'salt'			=> ( w * foods[i]['salt'] / 100.0 )
    }
    details << food_nutrition

    total_nutrition['energy']  += food_nutrition['energy']
    total_nutrition['protein'] += food_nutrition['protein']
    total_nutrition['fat']     += food_nutrition['fat']
    total_nutrition['carb']    += food_nutrition['carb']
    total_nutrition['salt']    += food_nutrition['salt']
  end

  # 文字列キーで統一
  nutrition_keys = ["energy", "protein", "fat", "carb", "salt"]
  nutrition_keys.each do |key|
  	fulfillment[key] = cfg.val[key] == 0.0 ? 0 : ( total_nutrition[key] / cfg.val[key] * 100 ).round( 1 )
  end
  
	return { 'fulfillment' => fulfillment, 'details' => details, 'total_nutrition' => total_nutrition }
end


def stock_result( dbr, weights, result, cfg )
	result_ = "#{cfg.base_jg()}::#{weights.join( '<>' )}::#{JSON.generate( result )}"
	token = issue_token( 32 )
	dbr.query( "INSERT INTO results SET user=?, base='detective', token=?, date=NOW(), result=?", true, [dbr.user.name, token, result_] )

  res = dbr.query( "SELECT COUNT(*) AS count FROM results WHERE user=? AND base='detective';", false, [dbr.user.name] )&.first
  current_count = res['count']

	if current_count > @result_limit
		delete_count = current_count - @result_limit
		dbr.query( "DELETE FROM results WHERE user=? AND base='detective' ORDER BY date ASC LIMIT ?", true, [dbr.user.name, delete_count] )
  end
end

#==============================================================================
# Main
#==============================================================================
html_init( nil )

user = User.new( @cgi )
user.debug if @debug
l = language_pack( user.language )
db = Db.new( user, @debug, false )
dbr = Dbr.new( user, @debug, false )
cfg = Config.new( user, 'detective' )

mod_list = mod_list( user )

puts "POST<br>" if @debug
command = @cgi['command']
code = @cgi['code']
past_result_token = @cgi['past_result_token']


####
html = ''
case command
when 'reasoning'
	puts 'REASONING<br>' if @debug

	puts 'Normalize target<br>' if @debug
	cfg.val['weight'] = @cgi['weight'].to_s == '' ? BigDecimal( '0' ) : BigDecimal( @cgi['weight'].to_s )
	cfg.val['energy'] = @cgi['energy'].to_s == '' ? BigDecimal( '0' ) : BigDecimal( @cgi['energy'].to_s )
	cfg.val['protein'] = @cgi['protein'].to_s == '' ? BigDecimal( '0' ) : BigDecimal( @cgi['protein'].to_s )
	cfg.val['fat'] = @cgi['fat'].to_s == '' ? BigDecimal( '0' ) : BigDecimal( @cgi['fat'].to_s )
	cfg.val['carb'] = @cgi['carb'].to_s == '' ? BigDecimal( '0' ) : BigDecimal( @cgi['carb'].to_s )
	cfg.val['salt'] = @cgi['salt'].to_s == '' ? BigDecimal( '0' ) : BigDecimal( @cgi['salt'].to_s )
	cfg.val['mode'] = @cgi['detective_mode'].to_s
	std_target, std_ratio = normalize_target( cfg )

	puts 'Get Food data from SUM<br>' if @debug
	foods = []
	res = db.query( "SELECT sum FROM #{$TB_SUM} WHERE user=?", false, [user.name] )&.first
	if res
		food = res['sum'].split( "\t" )

		if food.size == 0
			puts 'No Food'
			html = html_form_hints( @cgi, db, dbr, l, cfg, mod_list )
		else
			food.each do |e|
				sum_elements = e.split( ':' )

				food_no = sum_elements[0]
				fix_weight = sum_elements[0]
				fix_check = sum_elements[0]

				if /P|C/ =~ food_no
					rr = db.query( "SELECT ENERC_KCAL, PROTV, FATV, CHOV, NACL_EQ FROM #{$TB_FCTP} WHERE FN=?", false, [food_no] )
				elsif /U/ =~ food_no
					rr = db.query( "SELECT ENERC_KCAL, PROTV, FATV, CHOV, NACL_EQ FROM #{$TB_FCTP} WHERE FN=? AND user=?", false, [food_no, user.name] )
				else
					rr = db.query( "SELECT ENERC_KCAL, PROTV, FATV, CHOV, NACL_EQ FROM #{$TB_FCT} WHERE FN=?", false, [food_no] )
				end
				rr.each do |e|
					energy_ = BigDecimal( convert_zero( e['ENERC_KCAL'] ).to_s )
					protein_ = BigDecimal( convert_zero( e['PROTV'] ).to_s )
					fat_ = BigDecimal( convert_zero( e['FATV'] ).to_s )
					carb_ = BigDecimal( convert_zero( e['CHOV'] ).to_s )
					salt_ = BigDecimal( convert_zero( e['NACL_EQ'] ).to_s )
					fix_weight_ = BigDecimal( fix_weight.to_s )
					fix_check_ = fix_check
					foods << {
						'food_nos' => food_no.to_s,
						'energy' => energy_,
						'protein' => protein_,
						'fat' => fat_,
						'carb' => carb_,
						'salt' => salt_,
						'fix_weight' => fix_weight_,
						'fix_check' => fix_check_
					}
				end
			end


			p cfg.value( 'mode' ) if @debug
			mod = Object.const_get( "DetectiveMod_#{cfg.value('mode')}" )

			tuned_weights = mod.detective_module( foods, std_target, cfg )
			scale_back_weights = scale_back_weights( tuned_weights, cfg )
			result = calculate_fulfillment( foods, scale_back_weights, cfg )

			stock_result( dbr, scale_back_weights, result, cfg )

			html =  html_table_result( db, l, scale_back_weights, result, cfg )
			html << '<hr>'
			html << html_form_hints( @cgi, db, dbr, l, cfg, mod_list )
		end
	else
		puts 'ERROR'
		html = html_form_hints( @cgi, db, dbr, l, cfg, mod_list )
	end

when 'adopt'
	puts 'ADOPT<br>' if @debug
	food_nos = @cgi['food_nos_solid'].split( ':' )
	fw_ex = @cgi['fw_ex_solid'].split( ':' )
	new_sum = ''

	food_nos.each.with_index do |fn, i|
		new_sum << "#{fn}:#{fw_ex[i]}:g:#{fw_ex[i]}:::1.0:#{fw_ex[i]}\t"
	end
	new_sum.chop!

	db.query( "UPDATE #{$TB_SUM} set sum=? WHERE user=?", true, [new_sum, user.name] )

when 'load'
	puts 'LOAD<br>' if @debug
	res = dbr.query( "SELECT result FROM results WHERE base='detective' AND user=? AND token=?", false, [user.name, past_result_token] )&.first
	if res
		cfg_base_, weights, result_ = res['result'].split( '::' )
		scale_back_weights = weights.split( '<>' )
		result = JSON.parse( result_ )
		cfg.base_jp( cfg_base_ )

		html = html_table_result( db, l, scale_back_weights, result, cfg )
		html << '<hr>'
		html << html_form_hints( @cgi, db, dbr, l, cfg, mod_list )
	else
		html = '!'
	end
else
	if code != ''
		puts "FCZ import<br>" if @debug
		res = db.query( "SELECT origin, ENERC_KCAL, PROTV, FATV, CHOV, NACL_EQ FROM #{$TB_FCZ} WHERE code=? AND user=?", false, [code, user.name] )&.first
		if res
			cfg.val['weight'] = res['origin'] == '' ? BigDecimal( '0' ) : BigDecimal( res['origin'] ).round( 0 )
			cfg.val['energy'] = res['ENERC_KCAL'] == '' ? BigDecimal( '0' ) : BigDecimal( res['ENERC_KCAL'] )
			cfg.val['protein'] = res['PROTV'] == '' ? BigDecimal( '0' ) : BigDecimal( res['PROTV'] )
			cfg.val['fat'] = res['FATV'] == '' ? BigDecimal( '0' ) : BigDecimal( res['FATV'] )
			cfg.val['carb'] = res['CHOV'] == '' ? BigDecimal( '0' ) : BigDecimal( res['CHOV'] )
			cfg.val['salt'] = res['NACL_EQ'] == '' ? BigDecimal( '0' ) : BigDecimal( res['NACL_EQ'] )
		end
	end

	html = html_form_hints( @cgi, db, dbr, l, cfg, mod_list )
end

puts html


#==============================================================================
#POST PROCESS
#==============================================================================
if command == 'reasoning'
	p cfg.val if @debug
	cfg.update
end

#==============================================================================
#FRONT SCRIPT
#==============================================================================
if command == 'init'
	js = <<-"JS"
<script type='text/javascript'>

//
var reasoning = () => {
	const weight = document.getElementById( "weight" ).value;
	const energy = document.getElementById( "energy" ).value;
	const protein = document.getElementById( "protein" ).value;
	const fat = document.getElementById( "fat" ).value;
	const carb = document.getElementById( "carb" ).value;
	const salt = document.getElementById( "salt" ).value;
	const detective_mode = document.getElementById( "detective_mode" ).value;

	if( weight != '' && weight != '0' ){
		postLayer( '#{myself}', 'reasoning', true, 'L2', { weight, energy, protein, fat, carb, salt, detective_mode });
	}else{
		displayVIDEO( 'weight!(>_<)' );
	}
};

//
var detectiveAdopt = ( food_nos_solid, fw_ex_solid ) => {
		postLayer( '#{myself}', 'adopt', false, 'L2', { food_nos_solid, fw_ex_solid });

		displayREC();
		initCB( 'reload' );
};

//
var loadResult = () => {
	const past_result_token = document.getElementById( "past_result" ).value;
	postLayer( '#{myself}', 'load', true, 'L2', { past_result_token });
};

</script>
JS
	puts js

end

puts '(^q^)' if @debug
