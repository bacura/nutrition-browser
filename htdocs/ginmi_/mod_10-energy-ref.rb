# Ginmi module for basal metabolism reference 0.20b  (2024/04/11)
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
		weight = 0.0
		kexow = 0

		r = db.query( "SELECT bio FROM #{$TB_CFG} WHERE user='#{db.user.name}';", false )
		if r.first
			if r.first['bio'] != nil && r.first['bio'] != ''
				bio = JSON.parse( r.first['bio'] )
				birth = Time.parse( bio['birth'] )
				age = ( Date.today.strftime( "%Y%m%d" ).to_i - birth.strftime( "%Y%m%d" ).to_i ) / 10000
				sex = bio['sex'].to_i
				weight = bio['weight'].to_f
				kexow = bio['kexow'].to_i
			end
		end

		puts "IMPORT height & weight from KEX" if @debug
		if kexow == 1
			weight_flag = true
			r = db.query( "SELECT cell FROM #{$TB_KOYOMIEX} WHERE user='#{db.user.name}' AND cell !='' AND cell IS NOT NULL ORDER BY date DESC;", false )
			r.each do |e|
				kexc = JSON.parse( e['cell'] )
				if weight_flag && e['体重'] != nil
					weight = kexc['体重'].to_f
					weight_flag = false
				end

				break unless weight_flag
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
					<label class="input-group-text">#{'sex'}</label>
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
					<span class='input-group-text'>#{l['weight']}</span>
					<input type='text' class='form-control' id='weight' maxlength='6' value='#{weight.to_f}'>
				</div>
			</div>

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
			<div class='col-3'>
				<div class="input-group input-group-sm">
					<label class="input-group-text">妊婦・授乳婦</label>
					<select class="form-select form-select-sm" id="pregnancy">
						<option value='0'>-</option>
						<option value='1'>妊娠・初期</option>
						<option value='2'>妊娠・中期</option>
						<option value='3'>妊娠・後期</option>
						<option value='4'>授乳婦</option>
					</select>
				</div>
			</div>
			<div class='col'>
				※体重を0に設定すると参照体重を使用します。
			</div>
		</div>
		<br>

		<div class='row'>
			<button class='btn btn-sm btn-info' onclick="ginmiEnergyRefres()">#{l['calc']}</button>
		</div>
HTML
	when 'result'
		sex = cgi['sex'].to_i
		weight = BigDecimal( cgi['weight'] )
		age = cgi['age'].to_i
		pal = BigDecimal( cgi['pal'] )
		pregnancy = cgi['pregnancy'].to_i

		if false
			puts "sex:#{sex}<br>\n"
			puts "weight:#{weight}<br>\n"
			puts "age:#{age}<br>\n"
			puts "pal:#{pal}<br>\n"
			puts "pregnancy:#{pregnancy}<br>\n"
			puts "<hr>\n"
		end

		age_class = 0
		if age < 2
			age_class = 0
		elsif age < 5
			age_class = 1
		elsif age < 7
			age_class = 2
		elsif age < 8
			age_class = 3
		elsif age < 11
			age_class = 4
		elsif age < 14
			age_class = 5
		elsif age < 17
			age_class = 6
		elsif age < 29
			age_class = 7
		elsif age < 49
			age_class = 8
		elsif age < 69
			age_class = 9
		else
			age_class = 10
		end

		standard_male   = [61.0, 54.8, 44.3, 40.8, 37.4, 31.0 , 27.0, 24.0, 22.3, 21.5, 21.5]
		standard_female = [59.7, 52.2, 41.9, 38.3, 34.8, 29.6 , 25.3, 22.1, 21.7, 20.7, 20.7]

		ref_weiht_male   = [11.5, 16.5, 22.2, 28.0, 35.6, 49.0 , 59.7, 63.2, 68.5, 65.3, 60.0]
		ref_weiht_female = [11.0, 16.1, 21.9, 27.4, 36.3, 47.5 , 51.9, 50.0, 53.1, 53.0, 49.5]

		addtional = [150, 250, 450, 350]

		if weight == 0
			if sex == 0
				weight = ref_weiht_male[age_class]
			else
				weight = ref_weiht_female[age_class]
			end
		end

		formula = ''
		result = 0
		eer_formula = ''
		eer_result = 0
		if sex == 0
			result = ( standard_male[age_class] * weight ).round( 0 )
			formula = "#{standard_male[age_class]} * #{weight.to_f}"
			eer_result = ( standard_male[age_class] * weight * pal ).round( 0 )
			eer_formula = "#{standard_male[age_class]} * #{weight.to_f} * #{pal.to_f}"
		else
			if pregnancy == 0
				result = ( standard_female[age_class] * weight ).round( 0 )
				formula = "#{standard_female[age_class]} * #{weight.to_f}"
				eer_result = ( standard_female[age_class] * weight * pal ).round( 0 )
				eer_formula = "#{standard_female[age_class]} * #{weight.to_f} * #{pal.to_f}"
			else
				result = ( standard_female[age_class] * weight ).round( 0 )
				formula = "#{standard_female[age_class]} * #{weight.to_f}"
				eer_result = ( standard_female[age_class] * weight * pal + addtional[pregnancy] ).round( 0 )
				eer_formula = "#{standard_female[age_class]} * #{weight.to_f} * #{pal.to_f} + #{addtional[pregnancy]}"
			end
		end

html = <<-"HTML"
		<div class='row'>
			<div class='col-3'>基礎代謝量(kcal/day)</div>
			<div class='col-2'>#{result.to_i}</div>
			<div class='col-1'>計算式</div>
			<div class='col-4'>#{formula}</div>
		</div>
		<br>
		<div class='row'>
			<div class='col-3'>推定エネルギー必要量(kcal/day)</div>
			<div class='col-2'>#{eer_result.to_i}</div>
			<div class='col-1'>計算式</div>
			<div class='col-4'>#{eer_formula}</div>
		</div>
		<br>

HTML
	when 'save'

	end

	return html
end


def module_js( mod )
	js = <<-"JS"
<script type='text/javascript'>

var ginmiEnergyRefres = function(){
	var sex = document.getElementById( "sex" ).value;
	var age = document.getElementById( "age" ).value;
	var weight = document.getElementById( "weight" ).value;
	var pal = document.getElementById( "pal" ).value;
	var pregnancy = document.getElementById( "pregnancy" ).value;
	$.post( "ginmi.cgi", { mod:'#{mod}', command:'result', sex:sex, age:age, weight:weight, pal:pal, pregnancy:pregnancy }, function( data ){ $( "#L2" ).html( data );});

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
		'mod_name' => "基礎代謝量（参照値）",\
		'title' => "基礎代謝量計算（参照値）",\
		'age' => "年齢",\
		'sex' => "代謝的性別",\
		'male' => "男性",\
		'female' => "女性",\
		'height' => "身長(m)",\
		'weight' => "体重(kg)",\
		'pal' => "身体活動係数",\
		'calc' => "計 算"
	}

	return l[language]
end
