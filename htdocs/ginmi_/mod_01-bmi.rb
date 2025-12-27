# Ginmi module for BMI 0.11b (2024/04/09)
#encoding: utf-8

@debug = false

def ginmi_module( cgi, db )
	l = module_lp( db.user.language )
	module_js( cgi['mod'] )
	
	command = cgi['command']
	html = []

	case command
	when 'form'
		puts "Load bio config" if @debug
		age = 0
		height = 0.0
		weight = 0.0
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

		puts "IMPORT height & weight from KEX" if @debug
		if kexow == 1
			height_flag = true
			weight_flag = true
			r = db.query( "SELECT cell FROM #{$TB_KOYOMIEX} WHERE user='#{db.user.name}' AND cell !='' AND cell IS NOT NULL ORDER BY date DESC;", false )
			r.each do |e|
				kexc = JSON.parse( e['cell'] )
				if height_flag && e['身長'] != nil
					height = kexc['身長'].to_f / 100
					height_flag = false
				end
				if weight_flag && e['体重'] != nil
					weight = kexc['体重'].to_f
					weight_flag = false
				end

				break unless height_flag || weight_flag
			end
		end

		age_select = []
		if age < 50
			age_select[0] = 'SELECTED'
		elsif age < 70
			age_select[1] = 'SELECTED'
		else
			age_select[2] = 'SELECTED'
		end

		####
########
html[10] = <<-"HTML10"
<div class='row'>
<h5>#{l['title']}</h5>
</div>
<br>

<div class='row'>
	<div class='col-3'>
		<div class="input-group input-group-sm">
			<label class="input-group-text">#{l['age']}</label>
			<select class="form-select form-select-sm" id="age">
				<option value='18' #{age_select[0]}>18歳-49歳</option>
				<option value='50' #{age_select[1]}>50歳-69歳</option>
				<option value='70' #{age_select[2]}>70歳- </option>
			</select>
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
	<button class='btn btn-sm btn-info' onclick="ginmiBMIres()">#{l['calc']}</button>
</div>
HTML10
########
		####

	when 'result'
		age = cgi['age'].to_i
		weight = BigDecimal( cgi['weight'] )
		height = BigDecimal( cgi['height'] )
		if $DEBUG
			puts "age:#{age}<br>\n"
			puts "height:#{height}<br>\n"
			puts "weight:#{weight}<br>\n"
			puts "<hr>\n"
		end

		result = ( weight / ( height * height )).round( 1 )
		ibw = ( 22 * height * height ).round( 1 )

		age_1849 = []
		age_5069 = []
		age_70 = []
		hit_bg = [age_1849, age_5069, age_70]
		if age < 50
			if result < 18.5
				hit_bg[0][0] = 'bg-warning'
			elsif result < 25.0
				hit_bg[0][1] = 'bg-warning'
			elsif result < 30.0
				hit_bg[0][2] = 'bg-warning'
			elsif result < 35.0
				hit_bg[0][3] = 'bg-warning'
			elsif result < 40.0
				hit_bg[0][4] = 'bg-warning'
			else
				hit_bg[0][5] = 'bg-warning'
			end
		elsif age < 70
			if result < 20.0
				hit_bg[1][0] = 'bg-warning'
			elsif result < 25.0
				hit_bg[1][1] = 'bg-warning'
			elsif result < 30.0
				hit_bg[1][2] = 'bg-warning'
			elsif result < 35.0
				hit_bg[1][3] = 'bg-warning'
			elsif result < 40.0
				hit_bg[1][4] = 'bg-warning'
			else
				hit_bg[1][5] = 'bg-warning'
			end
		else
			if result < 21.5
				hit_bg[2][0] = 'bg-warning'
			elsif result < 25.0
				hit_bg[2][1] = 'bg-warning'
			elsif result < 30.0
				hit_bg[2][2] = 'bg-warning'
			elsif result < 35.0
				hit_bg[2][3] = 'bg-warning'
			elsif result < 40.0
				hit_bg[2][4] = 'bg-warning'
			else
				hit_bg[2][5] = 'bg-warning'
			end
		end

		#Degree of obesity
		obesity = (( weight - ibw ) / ibw * 100 ).round( 1 )
		obesity_hit_bg = []
		if obesity < -20
			obesity_hit_bg[0] = 'bg-warning'
		elsif obesity < -15
			obesity_hit_bg[1] = 'bg-warning'
		elsif obesity < 15
			obesity_hit_bg[2] = 'bg-warning'
		elsif obesity < 20
			obesity_hit_bg[3] = 'bg-warning'
		elsif obesity < 30
			obesity_hit_bg[4] = 'bg-warning'
		else
			obesity_hit_bg[5] = 'bg-warning'
		end

		####
########
html[20] = <<-"HTML20"
<div class='row'>
	<div class='col-2'>BMI値</div>
	<div class='col-2'>#{result.to_f}</div>
	<div class='col-2'>計算式</div>
	<div class='col-6'>#{weight.to_f} / ( #{height.to_f} * #{height.to_f} )</div>
</div>
<br>

<table class='table table-sm table-bordered'>
	<thead class='thead-light'>
		<tr>
			<th scope='col'>年齢</th>
			<th scope='col'>やせ</th>
			<th scope='col'>標準</th>
			<th scope='col'>肥満(I)</th>
			<th scope='col'>肥満(II)</th>
			<th scope='col'>肥満(III)</th>
			<th scope='col'>肥満(IV)</th>
		</tr>
	</thead>
	<tbody>
		<tr>
			<th scope='row'>18歳-49歳</th>
			<td class='#{hit_bg[0][0]}'> - 18.4</td>
			<td class='#{hit_bg[0][1]}'>18.5 - 24.9</td>
			<td class='#{hit_bg[0][2]}'>25.0 - 29.9</td>
			<td class='#{hit_bg[0][3]}'>30.0 - 34.9</td>
			<td class='#{hit_bg[0][4]}'>35.0 - 39.9</td>
			<td class='#{hit_bg[0][5]}'>40.0 - </td>
		</tr>
		<tr>
			<th scope='row'>50歳-69歳</th>
			<td class='#{hit_bg[1][0]}'> - 19.9</td>
			<td class='#{hit_bg[1][1]}'>20.0 - 24.9</td>
			<td class='#{hit_bg[1][2]}'>25.0 - 29.9</td>
			<td class='#{hit_bg[1][3]}'>30.0 - 34.9</td>
			<td class='#{hit_bg[1][4]}'>35.0 - 39.9</td>
			<td class='#{hit_bg[1][5]}'>40.0 - </td>
		</tr>
		<tr>
			<th scope='row'>70歳-</th>
			<td class='#{hit_bg[2][0]}'> - 21.4</td>
			<td class='#{hit_bg[2][1]}'>21.5 - 24.9</td>
			<td class='#{hit_bg[2][2]}'>25.0 - 29.9</td>
			<td class='#{hit_bg[2][3]}'>30.0 - 34.9</td>
			<td class='#{hit_bg[2][4]}'>35.0 - 39.9</td>
			<td class='#{hit_bg[2][5]}'>40.0 - </td>
		</tr>
	</tbody>
</table>
<br>

<div class='row'>
	<div class='col-2'>標準体重 (kg)</div>
	<div class='col-2'>#{ibw.to_f}</div>
	<div class='col-2'>計算式</div>
	<div class='col-6'>22 * #{height.to_f} * #{height.to_f}</div>
</div>
<br>

<div class='row'>
	<div class='col-2'>肥満度 (%)</div>
	<div class='col-2'>#{obesity.to_f}</div>
	<div class='col-2'>計算式</div>
	<div class='col-6'>( #{weight.to_f} - #{ibw.to_f} ) / #{ibw.to_f} * 100</div>
</div>
<br>

<table class='table table-sm table-bordered'>
	<thead class='thead-light'>
		<tr>
			<th scope='col'>やせすぎ</th>
			<th scope='col'>やけ</th>
			<th scope='col'>標準</th>
			<th scope='col'>ふとりぎみ</th>
			<th scope='col'>ややふとりすぎ</th>
			<th scope='col'>ふとりすぎ</th>
		</tr>
	</thead>
	<tbody>
		<tr>
			<td class='#{obesity_hit_bg[0]}'>-20%未満</td>
			<td class='#{obesity_hit_bg[1]}'>-15%未満</td>
			<td class='#{obesity_hit_bg[2]}'>-15%以上 +15%未満</td>
			<td class='#{obesity_hit_bg[3]}'>+15%以上</td>
			<td class='#{obesity_hit_bg[4]}'>+20%以上</td>
			<td class='#{obesity_hit_bg[5]}'>+30%以上</td>
		</tr>
	</tbody>
</table>
※区分は目安です。
HTML20
########
		####

	when 'save'

	end

	return html.join
end


def module_js( mod )
	js = <<-"JS"
<script type='text/javascript'>

var ginmiBMIres = function(){
	var age = document.getElementById( "age" ).value;
	var height = document.getElementById( "height" ).value;
	var weight = document.getElementById( "weight" ).value;
	$.post( "ginmi.cgi", { mod:'#{mod}', command:'result', age:age, height:height, weight:weight }, function( data ){
		$( "#L2" ).html( data );

		dl2 = true;
		displayBW();
	});

};


</script>
JS
	puts js
end

def module_lp( language )
	l = Hash.new
	l['ja'] = {
		'mod_name' => "BMI",\
		'title' => "BMI計算",\
		'age' => "年齢",\
		'height' => "身長(m)",\
		'weight' => "体重(kg)",\
		'calc' => "計　算"
	}

	return l[language]
end
