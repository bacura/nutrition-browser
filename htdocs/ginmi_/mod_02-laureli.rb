# Ginmi module for Laurel index 0.20b (2024/04/09)
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
		height = 0.0
		weight = 0.0
		kexow = 0

		r = db.query( "SELECT bio FROM #{$TB_CFG} WHERE user='#{db.user.name}';", false )
		if r.first
			if r.first['bio'] != nil && r.first['bio'] != ''
				bio = JSON.parse( r.first['bio'] )
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
					height = kexc['身長'].to_f
					height_flag = false
				end
				if weight_flag && e['体重'] != nil
					weight = kexc['体重'].to_f
					weight_flag = false
				end

				break unless height_flag || weight_flag
			end
		end

	html = <<-"HTML"
		<div class='row'>
		<h5>ローレル指数 計算</h5>
		</div>
		<br>

		<div class='row'>
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
			<button class='btn btn-sm btn-info' onclick="ginmiLaurelres()">#{l['calc']}</button>
		</div>
HTML
	when 'result'
		weight = BigDecimal( cgi['weight'] )
		height = BigDecimal( cgi['height'] )
		if false
			puts "height:#{height}<br>\n"
			puts "weight:#{weight}<br>\n"
			puts "<hr>\n"
		end

		result = ( weight / ( height * height * height ) * 10 ).round( 0 )

		ibw_index = 0.0
		hit_bg = ['', '', '', '', '', '', '']
		if result < 100
			hit_bg[0] = 'bg-warning'
		elsif result < 115
			hit_bg[1] = 'bg-warning'
		elsif result < 145
			hit_bg[2] = 'bg-warning'
		elsif result < 160
			hit_bg[3] = 'bg-warning'
		else
			hit_bg[4] = 'bg-warning'
		end

		ibw_index = 130
		ibw = ( ibw_index * ( height * height * height ) / 10 ) .round( 1 )

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

html = <<-"HTML"
		<div class='row'>
			<div class='col-2'>ローレル指数</div>
			<div class='col-2'>#{result.to_f}</div>
			<div class='col-2'>計算式</div>
			<div class='col-6'>#{weight.to_f} / ( #{height.to_f} * #{height.to_f} * #{height.to_f} ) * 10</div>
		</div>
		<br>

		<table width='50%' class='table table-sm table-bordered'>
			<thead class='thead-light'>
				<tr>
					<th scope='col'>年齢</th>
					<th scope='col'>やせすぎ</th>
					<th scope='col'>やせ気味</th>
					<th scope='col'>標準</th>
					<th scope='col'>太り気味</th>
					<th scope='col'>太りすぎ</th>
				</tr>
			</thead>
			<tbody>
				<tr>
					<th scope='row'>6歳-17歳</th>
					<td class='#{hit_bg[0]}'> - 99</td>
					<td class='#{hit_bg[1]}'>100 - 114</td>
					<td class='#{hit_bg[2]}'>115 - 144</td>
					<td class='#{hit_bg[3]}'>145 - 159</td>
					<td class='#{hit_bg[4]}'>160 - </td>
				</tr>

			</tbody>
		</table>
		<br>

		<div class='row'>
			<div class='col-2'>標準体重</div>
			<div class='col-2'>#{ibw.to_f}&nbsp;kg</div>
			<div class='col-2'>計算式</div>
			<div class='col-6'>#{ibw_index} * #{height.to_f} * #{height.to_f} * #{height.to_f} / 10</div>
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
HTML
	when 'save'

	end

	return html
end


def module_js( mod )
	js = <<-"JS"
<script type='text/javascript'>

var ginmiLaurelres = function(){
	var height = document.getElementById( "height" ).value;
	var weight = document.getElementById( "weight" ).value;
	$.post( "ginmi.cgi", { mod:'#{mod}', command:'result', height:height, weight:weight }, function( data ){ $( "#L2" ).html( data );});
	document.getElementById( "L2" ).style.display = 'block';
};

</script>
JS
	puts js
end

def module_lp( language )
	l = Hash.new
	l['ja'] = {
		'mod_name' => "ローレル指数",\
		'title' => "ローレル指数計算",\
		'age' => "年齢",\
		'height' => "身長(m)",\
		'weight' => "体重(kg)",\
		'calc' => "計　算"
	}

	return l[language]
end
