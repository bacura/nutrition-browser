# Ginmi module for Estimated height 0.00b (2024/04/11)
#encoding: utf-8

def ginmi_module( cgi, db )
	l = module_lp( db.user.language )
	module_js( cgi['mod'] )

	command = cgi['command']
	html = ''

	case command
	when 'form'
		sex = 0
		age = 18
		knee_height = 0

		puts "Load bio config" if @debug
		sex = 0
		age = 18
		kexow = 0
		r = db.query( "SELECT bio FROM #{$TB_CFG} WHERE user='#{db.user.name}';", false )
		if r.first
			if r.first['bio'] != nil && r.first['bio'] != ''
				bio = JSON.parse( r.first['bio'] )
				birth = Time.parse( bio['birth'] )
				age = ( Date.today.strftime( "%Y%m%d" ).to_i - birth.strftime( "%Y%m%d" ).to_i ) / 10000
				height = bio['height'].to_f
				weight = bio['weight'].to_f
				kexow = bio['kexow'].to_i
			end
		end

		sex_select = []
		if sex = 0
			sex_select[0] = 'SELECTED'
		else
			sex_select[1] = 'SELECTED'
		end


html = <<-"HTML"
		<div class='row'>
		<h5>推定身長 計算フォーム（Knee height法）</h5>
		</div>
		<br>

		<div class='row'>
			<div class='col-3'>
				<div class="input-group input-group-sm">
					<label class="input-group-text">身体的性別</label>
					<select class="form-select form-select-sm" id="sex">
						<option value='0' #{sex_select[0]}>男性</option>
						<option value='1' #{sex_select[1]}>女性</option>
					</select>
				</div>
			</div>

			<div class='col-3'>
				<div class='input-group input-group-sm'>
					<span class='input-group-text'>年齢</span>
					<input type='number' class='form-control' id='age' min='18' value='#{age}'>
				</div>
			</div>

			<div class='col-3'>
				<div class='input-group input-group-sm'>
					<span class='input-group-text'>膝下高(cm)</span>
					<input type='text' class='form-control' id='knee_height' value='#{knee_height}'>
				</div>
			</div>

		</div>
		<br>

		<div class='row'>
			<button class='btn btn-sm btn-info' onclick="Calculate()">計算</button>
		</div>
HTML
	when 'result'
		sex = cgi['sex'].to_i
		age = cgi['age'].to_i
		knee_height = BigDecimal( cgi['knee_height'] )

		if false
			puts "sex:#{sex}<br>\n"
			puts "age:#{age}<br>\n"
			puts "knee_height:#{knee_height}<br>\n"
			puts "<hr>\n"
		end

		result = 0.0
		formula = ''
		if sex == 0
			result = ( 64.19 - 0.04 * age + 2.02 * knee_height ).round( 1 )
			formula = "64.19 - 0.04 * #{age} + 2.02 * #{knee_height.to_f} "
		else
			result = ( 84.88 - 0.24 * age + 1.83 * knee_height ).round( 1 )
			formula = "84.88 - 0.24 * #{age} + 1.83 * #{knee_height.to_f}"
		end

html = <<-"HTML"
		<div class='row'>
			<div class='col-3'>推定身長(cm)</div>
			<div class='col-2'>#{result.to_f}</div>
			<div class='col-1'>計算式</div>
			<div class='col-6'>#{formula}</div>
		</div>
HTML
	when 'save'

	end

	return html
end


def module_js( mod )
	js = <<-"JS"
<script type='text/javascript'>

var Calculate = function(){
	var sex = document.getElementById( "sex" ).value;
	var age = document.getElementById( "age" ).value;
	var knee_height = document.getElementById( "knee_height" ).value;
	$.post( "ginmi.cgi", { mod:'#{mod}', command:'result', age:age, sex:sex, knee_height:knee_height }, function( data ){ $( "#L2" ).html( data );});
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
		'mod_name' => "身長推定",\
		'title' => "BMI計算",\
		'age' => "年齢",\
		'height' => "身長(m)",\
		'weight' => "体重(kg)",\
		'calc' => "計　算"
	}

	return l[language]
end
