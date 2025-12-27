# Ginmi module for basal metabolism 0.20b (2024/04/11)
#encoding: utf-8

@debug = false

def ginmi_module( cgi, db )
	l = module_lp( db.user.language )
	module_js( cgi['mod'] )

	command = cgi['command']
	html = ''

	case command
	when 'form'
		puts "Load bio config" if @debug
		sex = 0
		age = 0
		height = 0.0
		weight = 0.0
		kexow = 0

		r = db.query( "SELECT bio FROM #{$TB_CFG} WHERE user='#{db.user.name}';", false )
		if r.first
			if r.first['bio'] != nil && r.first['bio'] != ''
				bio = JSON.parse( r.first['bio'] )
				sex = bio['sex'].to_i
				birth = Time.parse( bio['birth'] )
				age = ( Date.today.strftime( "%Y%m%d" ).to_i - birth.strftime( "%Y%m%d" ).to_i ) / 10000
				height = bio['height'].to_f * 100
				weight = bio['weight'].to_f
				kexow = bio['kexow'].to_i
			end
		end

		puts "IMPORT height & weight from KEX" if @debug
		if kexow == 1
			height_flag = true
			weight_flag = true
			r = db.query( "SELECT cell FROM #{$TB_KOYOMIEX} WHERE user='#{db.user.name}' AND cell !='' AND cell IS NOT NULL ORDER BY date DESC;", false )
			r.each do |e|
				kexc = JSON.parse( e['cell'] )
				if height_flag && e['身長'] != nil
					height = kexc['身長'].to_f * 100
					height_flag = false
				end
				if weight_flag && e['体重'] != nil
					weight = kexc['体重'].to_f
					weight_flag = false
				end

				break unless height_flag || weight_flag
			end
		end

		sex_select = []
		if sex == 0
			sex_select[0] = 'SELECTED'
		else
			sex_select[1] = 'SELECTED'
		end


html = <<-"HTML"
		<div class='row'>
		<h5>#{l['title']}</h5>
		</div>
		<br>

		<div class='row'>
			<div class='col-3'>
				<div class="input-group input-group-sm">
					<label class="input-group-text">#{l['sex']}</label>
					<select class="form-select form-select-sm" id="sex">
						<option value='0' #{sex_select[0]}>#{l['male']}</option>
						<option value='1' #{sex_select[1]}>#{l['female']}</option>
					</select>
				</div>
			</div>

			<div class='col-3'>
				<div class='input-group input-group-sm'>
					<span class='input-group-text'>#{l['age']}</span>
					<input type='number' class='form-control' id='age' min='0' value='#{age}'>
				</div>
			</div>

			<div class='col-3'>
				<div class='input-group input-group-sm'>
					<span class='input-group-text'>#{l['height']}</span>
					<input type='text' class='form-control' id='height' maxlength='6' value='#{height}'>
				</div>
			</div>

			<div class='col-3'>
				<div class='input-group input-group-sm'>
					<span class='input-group-text'>#{l['weight']}</span>
					<input type='text' class='form-control' id='weight' maxlength='6' value='#{weight}'>
				</div>
			</div>
		</div>
		<br>
		<div class='row'>
			<div class='col-3'>
				<div class="input-group input-group-sm">
					<label class="input-group-text">#{l['pal']}</label>
					<select class="form-select form-select-sm" id="pal">
						<option value='1.50'>I (1.50)</option>
						<option value='1.75' SELECTED>II (1.75)</option>
						<option value='2.00'>III (2.00</option>
					</select>
				</div>
			</div>
		</div>
		<br>

		<div class='row'>
			<button class='btn btn-sm btn-info' onclick="ginmiEnergyHNres()">計算</button>
		</div>
HTML
	when 'result'
		sex = cgi['sex'].to_i
		age = cgi['age'].to_i
		weight = BigDecimal( cgi['weight'] )
		height = BigDecimal( cgi['height'] )
		pal = BigDecimal( cgi['pal'] )

		if false
			puts "sex:#{sex}<br>\n"
			puts "age:#{age}<br>\n"
			puts "height:#{height}<br>\n"
			puts "weight:#{weight}<br>\n"
			puts "pal:#{pal}<br>\n"
			puts "<hr>\n"
		end

		result = 0
		formula = ''
		if sex == 0
			result = (( 0.0481 * weight + 0.0234 * height - 0.0138 * age - 0.4235 ) * 1000 / 4.186 ).round( 0 )
			formula = "( 0.0481 * #{weight.to_f} + 0.0234 * #{height.to_f} - 0.0138 * #{age} - 0.4235 ) * 1000 / 4.186"
		else
			result = (( 0.0481 * weight + 0.0234 * height - 0.0138 * age - 0.9708 ) * 1000 / 4.186 ).round( 0 )
			formula = "( 0.0481 * #{weight.to_f} + 0.0234 * #{height.to_f} - 0.0138 * #{age} - 0.9708 ) * 1000 / 4.186"
		end
		eer_result = ( result * pal ).round( 0 )
		eer_formula = "#{result.to_i} * #{pal.to_f}"


		ibw = ( 22 * height * height / 10000 ).round( 1 )
		ibw_result = 0
		ibw_formula = ''
		if sex == 0
			ibw_result = (( 0.0481 * ibw + 0.0234 * height - 0.0138 * age - 0.4235 ) * 1000 / 4.186 ).round( 0 )
			ibw_formula = "( 0.0481 * #{ibw.to_f} + 0.0234 * #{height.to_f} - 0.0138 * #{age} - 0.4235 ) * 1000 / 4.186"
		else
			ibw_result = (( 0.0481 * ibw + 0.0234 * height - 0.0138 * age - 0.9708 ) * 1000 / 4.186 ).round( 0 )
			ibw_formula = "( 0.0481 * #{ibw.to_f} + 0.0234 * #{height.to_f} - 0.0138 * #{age} - 0.9708 ) * 1000 / 4.186"
		end
		ibw_eer_result = ( ibw_result * pal ).round( 0 )
		ibw_eer_formula = "#{ibw_result.to_i} * #{pal.to_f}"

html = <<-"HTML"
		<div class='row'>
			<div class='col-3'>基礎代謝量(kcal/day)</div>
			<div class='col-2'>#{result.to_i}</div>
			<div class='col-1'>計算式</div>
			<div class='col-6'>#{formula}</div>
		</div>
		<br>
		<div class='row'>
			<div class='col-3'>推定エネルギー必要量(kcal/day)</div>
			<div class='col-2'>#{eer_result.to_i}</div>
			<div class='col-1'>計算式</div>
			<div class='col-6'>#{eer_formula}</div>
		</div>
		<hr>

		<div class='row'>
			<div class='col-3'>標準体重(kg)</div>
			<div class='col-2'>#{ibw.to_f}</div>
		</div>
		<br>
		<div class='row'>
			<div class='col-3'>基礎代謝量(kcal/day)</div>
			<div class='col-2'>#{ibw_result.to_i}</div>
			<div class='col-1'>計算式</div>
			<div class='col-6'>#{ibw_formula}</div>
		</div>
		<br>
		<div class='row'>
			<div class='col-3'>推定エネルギー必要量(kcal/day)</div>
			<div class='col-2'>#{(ibw_eer_result.to_i)}</div>
			<div class='col-1'>計算式</div>
			<div class='col-6'>#{ibw_eer_formula}</div>
		</div>

HTML
	when 'save'

	end

	return html
end


def module_js( mod )
	js = <<-"JS"
<script type='text/javascript'>

var ginmiEnergyHNres = function(){
	var sex = document.getElementById( "sex" ).value;
	var age = document.getElementById( "age" ).value;
	var height = document.getElementById( "height" ).value;
	var weight = document.getElementById( "weight" ).value;
	var pal = document.getElementById( "pal" ).value;
	$.post( "ginmi.cgi", { mod:'#{mod}', command:'result', age:age, sex:sex, height:height, weight:weight, pal:pal }, function( data ){ $( "#L2" ).html( data );});

	dl2 = true;
	displayBW();
};


</script>
JS
	puts js
end

def module_lp( language )
	l = Hash.new
	l['ja'] = {
		'mod_name' => "基礎代謝量（国立健康・栄養研究所の式）",\
		'title' => "基礎代謝量計算（国立健康・栄養研究所の式）",\
		'age' => "年齢",\
		'sex' => "代謝的性別",\
		'male' => "男性",\
		'female' => "女性",\
		'height' => "身長(cm)",\
		'weight' => "体重(kg)",\
		'pal' => "身体活動係数",\
		'calc' => "計　算"
	}

	return l[language]
end
