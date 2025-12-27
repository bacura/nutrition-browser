#! /usr/bin/ruby
#encoding: utf-8
#Nutrition browser 2020 recipe 3D plotter 0.1.1.AI (2025/02/17)


#==============================================================================
# STATIC
#==============================================================================
@debug = false
myself = File.basename( __FILE__ )

#==============================================================================
# LIBRARY
#==============================================================================
require './soul'

#==============================================================================
# DEFINITION
#==============================================================================

# Language pack
def language_pack( language )
	l = Hash.new

	#Japanese
	l['ja'] = {
		recipe3ds:	"レシピ プロット",
		all: 		"全て",
		all_ns:		"全て（ー調味系）",
		draft:		"仮組",
		protect: 	"保護",
		public: 	"公開",
		normal: 	"無印",
		favoriter: 	"お気に入り",
		publicou: 	"公開(他ユーザー)",
		type:	 	"料理スタイル",
		role: 		"献立区分",
		tech:	 	"調理区分",
		chomi:	 	"[ 調味％ ]",
		range:		"表示範囲",
		style:		"料理スタイル",
		time:		"表目安時間(分)",
		cost:		"目安費用(円)",
		no_def:		"未設定",
		plot_size:	"表示サイズ",
		x_log:		"X軸Log",
		y_log: 		"Y軸Log",
		x_zoom: 	"X軸Zoom",
		y_zoom: 	"Y軸Zoom",
		more:		"％以上の範囲",
		less:		"％未満の範囲",
		xcomp:		"X成分",
		ycomp:		"Y成分",
		zcomp:		"Z範囲",
		reset:		"リセット",
		plot:		"プ ロ ッ ト",
		plot_num:	"プロット数", 
		item:		"栄養成分",
		unit:		"単位",
		average:	"平均値",
		median:		"中央値",
		min:		"最小値",
		max:		"最大値",
		crosshair2:	"<img src='bootstrap-dist/icons/crosshair2-red.svg' style='height:2.0em; width:2.0em;'>"
	}

	return l[language]
end

#### Display range
def range_html( range, l )
	range_select = []
	7.times do |i| range_select[i] = $SELECT[range == i] end

	html = l[:range]
	html << '<select class="form-select form-select-sm" id="range">'
	html << "<option value='0' #{range_select[0]}>#{l[:all]}</option>"
	html << "<option value='1' #{range_select[1]}>#{l[:favoriter]}</option>"
	html << "<option value='2' #{range_select[2]}>#{l[:draft]}</option>"
	html << "<option value='3' #{range_select[3]}>#{l[:protect]}</option>"
	html << "<option value='4' #{range_select[4]}>#{l[:public]}</option>"
	html << "<option value='5' #{range_select[5]}>#{l[:normal]}</option>"
	html << "<option value='6' #{range_select[6]}>#{l[:publicou]}</option>"
	html << '</select>'

	return html
end

#### 料理スタイル生成
def type_html( type, l )
	html = l[:type]
	html << '<select class="form-select form-select-sm" id="type">'
	html << "<option value='99'>#{l[:all]}</option>"
	@recipe_type.size.times do |c|
		html << "<option value='#{c}' #{$SELECT[type == c]}>#{@recipe_type[c]}</option>"
	end
	html << '</select>'

	return html
end

#### 献立区分
def role_html( role, l )
	html = l[:role]
	html << '<select class="form-select form-select-sm" id="role">'
	html << "<option value='99'>#{l[:all]}</option>"
	html << "<option value='98' #{$SELECT[role == 98]}>#{l[:all_ns]}</option>"
	@recipe_role.size.times do |c|
		html << "<option value='#{c}' #{$SELECT[role == c]}>#{@recipe_role[c]}</option>"
	end
	html << "<option value='100' #{$SELECT[role == 100]}>#{l[:chomi]}</option>"
	html << '</select>'

	return html
end

#### 調理区分
def tech_html( tech, l )
		html = l[:tech]
	html << '<select class="form-select form-select-sm" id="tech">'
	html << "<option value='99'>#{l[:all]}</option>"
	@recipe_tech.size.times do |c|
		html << "<option value='#{c}' #{$SELECT[tech == c]}>#{@recipe_tech[c]}</option>"
	end
	html << '</select>'

	return html
end

#### 目安時間
def time_html( time, l )
	html = l[:time]
	html << '<select class="form-select form-select-sm" id="time">'
	html << "<option value='99'>#{l[:all]}</option>"
	@recipe_time.size.times do |c|
		html << "<option value='#{c}' #{$SELECT[time == c]}>#{@recipe_time[c]}</option>"
	end
	html << '</select>'

	return html
end

#### 目安費用
def cost_html( cost, l )
	html = l[:cost]
	html << '<select class="form-select form-select-sm" id="cost">'
	html << "<option value='99'>#{l[:all]}</option>"
	@recipe_cost.size.times do |c|
		html << "<option value='#{c}' #{$SELECT[cost == c]}>#{@recipe_cost[c]}</option>"
	end
	html << '</select>'

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
cfg = Config.new( user, 'recipe-list' )

#### POST
command = @cgi['command']
if @debug
	puts "command: #{command}<br>"
	puts "<hr>"
end


#### 検索条件設定
cfg.val['page'] = cfg.val['page'].to_i == 0 ? 1 : cfg.val['page'].to_i
cfg.val['page_limit'] = cfg.val['page_limit'].nil? ? limit_num : cfg.val['page_limit'].to_i
cfg.val['range'] = cfg.val['range'].nil?  ? 0 : cfg.val['range'].to_i
cfg.val['type'] = cfg.val['type'].nil? ? 99 : cfg.val['type'].to_i
cfg.val['role'] = cfg.val['role'].nil? ? 99 : cfg.val['role'].to_i
cfg.val['tech'] = cfg.val['tech'].nil? ? 99 : cfg.val['tech'].to_i
cfg.val['time'] = cfg.val['time'].nil? ? 99 : cfg.val['time'].to_i
cfg.val['cost'] = cfg.val['cost'].nil? ? 99 : cfg.val['cost'].to_i

cfg.val['xitem'].nil? ? 'ENERC' : cfg.val['xitem']
cfg.val['yitem'].nil? ? 'ENERC' : cfg.val['yitem']
cfg.val['zitem'].nil? ?  'ENERC' : cfg.val['zitem']
cfg.val['zml'].nil? ? 0 : cfg.val['zml'].to_i
cfg.val['zrange'].nil? ? 0 : cfg.val['zrange'].to_i
cfg.val['area_size'].nil? ? 0.6 : cfg.val['area_size'].to_f
cfg.val['x_zoom'].nil? ? 'false' : cfg.val['x_zoom'].to_s
cfg.val['y_log'].nil? ? 'linner' : cfg.val['y_log'].to_s


case command
when 'plott_area'
	area_size_option = ''
	area_size_value = [ 0.7, 0.5, 0.4, 0.3 ]
	area_size_text = %w( Max Large Medium Small )
	4.times do |c|
		area_size_option << "<option value='#{area_size_value[c]}' #{$SELECT[area_size_value[c] == cfg.val['area_size']]}>#{area_size_text[c]}</option>"
	end

html = <<-"PLOTT"
	<div class="row">
		<div class='col-2'>
			#{l[:plot_size]}<br>
			<select class="form-select form-select-sm" id="area_size" onchange="resize3dp()">
				#{area_size_option}
			</select>
			<br>
			<br>

<!--			<div class="form-check form-switch">
				<label class="form-check-label">#{l[:x_log]}</label>
				<input class="form-check-input" type="checkbox" id="x_log" DISABLED>
			</div>
			<br>
			<br>
-->
			<div class="form-check form-switch">
				<label class="form-check-label">#{l[:x_zoom]}</label>
				<input class="form-check-input" type="checkbox" id="x_zoom" onchange="recipe3dsPlottDraw()" #{$CHECK[cfg.val['x_zoom'] == 'true']}>
			</div>
			<br>
			<br>

			<div class="form-check form-switch">
				<label class="form-check-label">#{l[:y_log]}</label>
				<input class="form-check-input" type="checkbox" id="y_log" onchange="recipe3dsPlottDraw()" #{$CHECK[cfg.val['y_log'] == 'log']}>
			</div>
			<br>
			<br>
<!--
			<div class="form-check form-switch">
				<label class="form-check-label">#{l[:y_zoom]}</label>
				<input class="form-check-input" type="checkbox" id="y_zoom" DISABLED>
			</div>
-->
		</div>
		<div class='col-10'>
			<div id='recipe3ds_plott' align='center'></div>
		</div>
	</div>


PLOTT

when 'plott_data', 'monitor', 'config'
	cfg.val['range'] = @cgi['range'].to_i
	cfg.val['type'] = @cgi['type'].to_i
	cfg.val['role'] = @cgi['role'].to_i
	cfg.val['tech'] = @cgi['tech'].to_i
	cfg.val['time'] = @cgi['time'].to_i
	cfg.val['cost'] = @cgi['cost'].to_i

	cfg.val['xitem'] = @cgi['xitem']
	cfg.val['yitem'] = @cgi['yitem']
	cfg.val['zitem'] = @cgi['zitem']
	cfg.val['zml'] = @cgi['zml'].to_i
	cfg.val['zrange'] = @cgi['zrange'].to_i

	cfg.val['area_size'] = @cgi['area_size'].to_f
	cfg.val['x_zoom'] = @cgi['x_zoom']
	cfg.val['y_log'] = @cgi['y_log'].to_s

	if command == 'config'
		cfg.update()
		exit
	end

when 'reset'
	cfg.val['range'] = 0
	cfg.val['type'] = 99
	cfg.val['role'] = 99
	cfg.val['tech'] = 99
	cfg.val['time'] = 99
	cfg.val['cost'] = 99

	cfg.val['xitem'] = 'ENERC'
	cfg.val['yitem'] = 'ENERC'
	cfg.val['zitem'] = 'ENERC'
	cfg.val['zml'] = 0
	cfg.val['zrange'] = 0

	cfg.val['area_size'] = 0.6
	cfg.val['x_zoom'] = 'false'
	cfg.val['y_log'] = 'linner'
when 'config'

end
p cfg.val if @debug

xitems = []
yitems = []
zitems = []
names = []
codes = []

# WHERE setting
t1 = "#{$TB_RECIPE}"
t2 = "#{$TB_FCZ}"

sql_where = 'WHERE '
case cfg.val['range']
# 自分の全て
when 0
	sql_where << "t1.user='#{user.name}' AND t1.name!=''"
# 自分のお気に入り
when 1
	sql_where << "t1.user='#{user.name}' AND t1.name!='' AND t1.favorite='1'"
# 自分の下書き
when 2
	sql_where << "t1.user='#{user.name}' AND t1.name!='' AND t1.draft='1'"
# 自分の保護
when 3
	sql_where << "t1.user='#{user.name}' AND t1.name!='' AND t1.protect='1'"
# 自分の公開
when 4
	sql_where << "t1.user='#{user.name}' AND t1.name!='' AND t1.public='1'"
# 自分の無印
when 5
	sql_where << "t1.user='#{user.name}' AND t1.name!=''AND t1.public='0'AND t1.draft='0'"
# 他の公開
when 6
	sql_where << "t1.user!='#{user.name}' AND t1.name!=''AND t1.public='1'"
else
	sql_where << "t1.user='#{user.name}' AND t1.name!=''"
end

#料理スタイル
sql_where << " AND t1.type='#{cfg.val['type']}'" unless cfg.val['type'] == 99
#献立区分
if cfg.val['role'] == 98
	sql_where << " AND t1.role!='100' AND t1.role!='7'"
elsif cfg.val['role'] != 99
	sql_where << " AND t1.role='#{cfg.val['role']}'"
end

sql_where << " AND t1.tech='#{cfg.val['tech']}" unless cfg.val['tech'] == 99
sql_where << " AND t1.time>0 AND t1.time<=#{cfg.val['time']}" unless cfg.val['time'] == 99
sql_where << " AND t1.cost>0 AND t1.cost<=#{cfg.val['cost']}" unless cfg.val['cost'] == 99

#Z成分カットオフ
r = db.query( "SELECT count(*) FROM #{$TB_RECIPE} AS t1 LEFT JOIN #{$TB_FCZ} AS t2 ON t1.code=t2.origin #{sql_where};", false )
spot_num = r.first['count(*)']
percent = cfg.val['zrange'].to_f / 100
elements_count = ( spot_num * percent ).floor
if cfg.val['zml'] == 1
	sql_where << " ORDER BY t2.#{cfg.val['zitem']} LIMIT #{elements_count - 1}"
elsif cfg.val['zml'] == 0
	sql_where << " ORDER BY t2.#{cfg.val['zitem']} LIMIT #{spot_num - elements_count} OFFSET #{elements_count}"
end


case command
when 'plott_area'
when 'plott_data'
	r = db.query( "SELECT t1.name, t1.code, t2.#{cfg.val['xitem']}, t2.#{cfg.val['yitem']} FROM #{$TB_RECIPE} AS t1 LEFT JOIN #{$TB_FCZ} AS t2 ON t1.code=t2.origin #{sql_where};", false )
	if  r.first
		r.each do |e|
			xitems << convert_zero( e[cfg.val['xitem']] ).to_f.round( 1 )
			yitems << convert_zero( e[cfg.val['yitem']] ).to_f.round( 1 )
			nt = e['name']
			nt.gsub!( '(', '（')
			nt.gsub!( ')', '）')
			nt.gsub!( ':', '：')
			names << nt
			codes << e['code']
		end

		TICK_VALUES = [
		  [1, [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]],
		  [5, [0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0]],
		  [10, [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]],
		  [50, [0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50]],
		  [100, [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]],
		  [500, [0, 50, 100, 150, 200, 250, 300, 350, 400, 450, 500]],
		  [1000, [0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000]],
		  [5000, [0, 500, 1000, 1500, 2000, 2500, 3000, 3500, 4000, 4500, 5000]],
		  [10000, [0, 1000, 2000, 3000, 4000, 5000, 6000, 7000, 8000, 9000, 10000]],
		  [50000, [0, 5000, 10000, 15000, 20000, 25000, 30000, 35000, 40000, 45000, 50000]],
		  [Float::INFINITY, [0, 10000, 20000, 30000, 40000, 50000, 60000, 70000, 80000, 90000, 100000]]
		]

		x_tickv = TICK_VALUES.find { |limit, _| xitems.max < limit }[1]
		y_tickv = TICK_VALUES.find { |limit, _| yitems.max < limit }[1]

		label_x = @fct_name[cfg.val['xitem']].split( '(' )[0]
		label_x = "#{label_x} (#{@fct_unit[cfg.val['xitem']]})" 
		label_y = @fct_name[cfg.val['yitem']].split( '(' )[0]
		label_y = "#{label_y} (#{@fct_unit[cfg.val['yitem']]})" 
		if label_x == label_y
			label_x = label_x + '_x'
			label_y = label_y + '_y'
		end

		raw = []
		raw[0] = xitems.unshift( label_x ).join( ',' )
		raw[1] = yitems.unshift( label_y ).join( ',' )
		raw[2] = names.unshift( 'recipe_name' ).join( ',' )
		raw[3] = codes.unshift( 'recipe_code' ).join( ',' )
		raw[4] = x_tickv.join( ',' )
		raw[5] = y_tickv.join( ',' )

		puts raw.join( '::' )

	else
		puts '0'
	end


when 'monitor'
	items = {
	  x: { values: [], key: cfg.val['xitem'], label: '[x]' },
	  y: { values: [], key: cfg.val['yitem'], label: '[y]' },
	  z: { values: [], key: cfg.val['zitem'], label: '[z]' }
	}

	r = db.query( "SELECT t1.name, t1.code, t2.#{items[:x][:key]}, t2.#{items[:y][:key]}, t2.#{items[:z][:key]} FROM #{$TB_RECIPE} AS t1 LEFT JOIN #{$TB_FCZ} AS t2 ON t1.code=t2.origin #{sql_where};", false )
	r.each do |e|
	  items.each do |axis, data| data[:values] << convert_zero( e[data[:key]] ).to_f.round( 1 ) end
	end

	puts "<h5>#{l[:plot_num]}：#{r.size}</h5>"
	puts "<table class='table'>"
	puts "  <tr><td>#{l[:item]}</td><td>#{l[:unit]}</td><td>#{l[:average]}</td><td>#{l[:median]}</td><td>#{l[:min]}</td><td>#{l[:max]}</td></tr>"

	items.each do |axis, data|
	  sorted = data[:values].sort
	  average = ( data[:values].sum / data[:values].size.to_f ).round( 1 )
	  median = sorted.size.odd? ? sorted[sorted.size / 2] : (( sorted[sorted.size / 2 - 1] + sorted[sorted.size / 2] ) / 2.0 ).round( 1 )

	  puts "  <tr><td>#{data[:label]} #{@fct_name[data[:key]]}</td><td>#{@fct_unit[data[:key]]}</td><td>#{average}</td><td>#{median}</td><td>#{data[:values].min}</td><td>#{data[:values].max}</td></tr>"
	end

	puts "</table>"
	puts html

else
	#### 検索条件HTML
	html_range = range_html( cfg.val['range'], l )
	html_type = type_html( cfg.val['type'], l )
	html_role = role_html( cfg.val['role'], l )
	html_tech = tech_html( cfg.val['tech'], l )
	html_time = time_html( cfg.val['time'], l )
	html_cost = cost_html( cfg.val['cost'], l )

	####
	xselect = '<select class="form-select" id="xitem">'
	@fct_item.each.with_index do |e, i|
		unless e == 'FG' || e == 'FN' || e == 'SID' || e == 'Tagnames' || e == 'REFUSE' || e == 'Notice'
			xselect << "<option value='#{e}' #{$SELECT[e == cfg.val['xitem']]}>#{@fct_name[e]}</option>"
		end
	end
	xselect << '</select>'

	yselect = '<select class="form-select" id="yitem">'
	@fct_item.each do |e|
		unless e == 'FG' || e == 'FN' || e == 'SID' || e == 'Tagnames' || e == 'REFUSE' || e == 'Notice'
			yselect << "<option value='#{e}' #{$SELECT[e == cfg.val['yitem']]}>#{@fct_name[e]}</option>"
		end
	end
	yselect << '</select>'

	zselect = '<select class="form-select" id="zitem">'
	@fct_item.each do |e|
		unless e == 'FG' || e == 'FN' || e == 'SID' || e == 'Tagnames' || e == 'REFUSE' || e == 'Notice'
			zselect << "<option value='#{e}' #{$SELECT[e == cfg.val['zitem']]}>#{@fct_name[e]}</option>"
		end
	end
	zselect << '</select>'

	zml_select = '<select class="form-select" id="zml">'
	zml_select << "<option value='0' >#{l[:more]}</option>"
	zml_select << "<option value='1' #{$SELECT[cfg.val['zitem']]}>#{l[:less]}</option>"
	zml_select << '</select>'

	puts "Control HTML<br>" if @debug
	html = <<-"HTML"
<div class='container-fluid'>
	<div class='row'>
		<div class='col-5'><h5>#{l[:recipe3ds]}</h5></div>
		<div class='col-2' align='center'><span onclick='recipeList( "init" )'>#{l[:crosshair2]}</span></div>
	</div>
	<div class='row'>
		<div class='col'>#{html_range}</div>
		<div class='col'>#{html_type}</div>
		<div class='col'>#{html_role}</div>
		<div class='col'>#{html_tech}</div>
		<div class='col'>#{html_time}</div>
		<div class='col'>#{html_cost}</div>
	</div>
	<br>
	<div class='row'>
		<div class='col-3'>
			<div class="input-group input-group-sm mb-3">
				<label class="input-group-text">#{l[:xcomp]}</label>
				#{xselect}
			</div>
		</div>
		<div class='col-3'>
			<div class="input-group input-group-sm  mb-3">
				<label class="input-group-text">#{l[:ycomp]}</label>
				#{yselect}
			</div>
		</div>
		<div class='col-3'>
			<div class="input-group input-group-sm  mb-3">
				<label class="input-group-text">#{l[:zcomp]}</label>
				#{zselect}
			</div>
		</div>
		<div class='col-3'>
			<div class="input-group input-group-sm mb-3">
				<input type="number" class="form-control" min="0"  max="100" value="0" step="10" id='zrange'>
				#{zml_select}
			</div>
		</div>
	</div>
	<div class='row'>
		<div class='col-11'>
			<div class='row'>
				<button class="btn btn-info btn-sm" type="button" onclick="recipe3dsPlottDraw()">#{l[:plot]}</button>
			</div>
		</div>
		<div class='col-1' align="right">
			<button class="btn btn-warning btn-sm" type="button" onclick="recipe3dsReset()">#{l[:reset]}</button>
		</div>
	</div>
	<br>
</div>
HTML

end

puts html

#==============================================================================
#POST PROCESS
#==============================================================================

if command == 'monitor'
	#### 検索設定の保存
#	p cfg.val
	cfg.update()
end

#==============================================================================
#FRONT SCRIPT
#==============================================================================

if command == 'init'

	js = <<~JS
<script type='text/javascript'>

var postReq_recipe3ds = ( command, data, successCallback ) => {
	$.post( '#{myself}', { command, ...data })
		.done( successCallback )
		.fail(( jqXHR, textStatus, errorThrown ) => {
			console.error( "Request failed: ", textStatus, errorThrown );
			alert( "An error occurred. Please try again." );
		}
	);
};


// Dosplaying recipe by scatter plott
var recipe3dsPlottDraw = function(){
	const range = $( "#range" ).val();
	const type = $( "#type" ).val();
	const role = $( "#role" ).val();
	const tech = $( "#tech" ).val();
	const time = $( "#time" ).val();
	const cost = $( "#cost" ).val();

	const xitem = $( "#xitem" ).val();
	const yitem = $( "#yitem" ).val();
	const zitem = $( "#zitem" ).val();
	const zml = $( "#zml" ).val();
	const zrange = $( "#zrange" ).val();

	const area_size = $( "#area_size" ).val();
	const x_zoom = $( "#x_zoom" ).prop( "checked" );
	const y_log  = $( "#y_log" ).prop( "checked" ) ? 'log' : 'linear';

	postReq_recipe3ds( 'monitor', { range, type, role, tech, time, cost,
		xitem, yitem, zitem, zml, zrange, area_size, x_zoom, y_log }, data => {
		$( "#L3" ).html( data );
	});

	postReq_recipe3ds( 'plott_data', { range, type, role, tech, time, cost,
		xitem, yitem, zitem, zml, zrange, area_size, x_zoom, y_log }, raw => {

		//
		if( raw == 0 ){
			displayVIDEO( 'No match found' );
			return;
		}

		//
		const column = ( String( raw )).split( '::' );
		const x_values = ( String( column[0] )).split(',');
		const y_values = ( String( column[1] )).split(',');
		const names = ( String( column[2] )).split(',');
		const codes = ( String( column[3] )).split(',');
		const x_tickv = ( String( column[4] )).split(',');
		const y_tickv = ( String( column[5] )).split(',');

		//
		let names_dic = {};
		let codes_dic = {};
		for( let i = 0; i < x_values.length; i++ ){
			names_dic[ x_values[i] + y_values[i]] = names[ i ]; 
			codes_dic[ x_values[i] + y_values[i]] = codes[ i ];
		}

		//
		const plott_size = $( document.documentElement ).width();
		const frame_rate = $( "#area_size" ).val();
		if ( window.chart_recipe3d != null ){
			window.chart_recipe3d.destroy();
			displayVIDEO( 'Flush!' );
		}

		//
		window.chart_recipe3d = c3.generate({
			bindto: '#recipe3ds_plott',
			size:{ width: plott_size * frame_rate, height: plott_size * frame_rate },

			data: {
				columns: [
					x_values,	// x軸
					y_values	// y軸
				],
			    x: x_values[0],
				type: 'scatter',
				onclick: function ( d ){
					var key = d.x.toFixed( 1 ) + d.value.toFixed( 1 );
					searchDR(  codes_dic[ key ] );
                }
//				colors:{ x_values[0]: '#ff44FF' }
			},
			axis: {
			    x: {
			    	type: 'linear',
			    	label: x_values[0],
			    	min:0,
					tick: {
						fit: true,
						count: 10,
						format: d3.format( "d" ),
						values: x_tickv
					},
					padding: { left: 0, right: 10 }
				},
			    y: {
			    	label: y_values[0],
			    	type: y_log,
			    	min: 0,
					tick: {
						fit: true,
						count: 10,
						format: d3.format( "d" ),
						values: y_tickv
					},
			  		padding: { top: 10, bottom: 0 }
			    }
			},
			zoom: { enabled: x_zoom },
			point: {
				r: 5,
				focus: { expand: { r: 8 }}
			 },
			grid: {
     			x: { show: true },
        		y: { show: true }
            },
			legend: { show: false },
			tooltip: {
				grouped: false,
				contents: function ( d, defaultTitleFormat, defaultValueFormat, color ) {
					var tooltip_html = '<table style="background-color:#ffffff; font-size:1.5em;">';
					var key = d[0].x.toFixed( 1 ) + d[0].value.toFixed( 1 );
					tooltip_html += '<tr><td colspan="2"  style="background-color:mistyrose;">' + names_dic[ key ] + '</td></tr>'
					tooltip_html += '<tr><td>' + x_values[0] + '</td><td>: ' + d[0].x + '</td></tr>'
					tooltip_html += '<tr><td>' + y_values[0] + '</td><td>: ' + d[0].value + '</td></tr>'
					tooltip_html += '</table>'

					return tooltip_html;
				}
			},
		});
		resize3dp();
	});
};


// Dosplaying recipe by scatter plott
var recipe3dsReset = function(){
	$( "#range" ).val( 0 );
	$( "#type" ).val( 99 );
	$( "#role" ).val( 99);
	$( "#tech" ).val( 99 );
	$( "#time" ).val( 99 );
	$( "#cost" ).val( 99 );

	$( "#xitem" ).val( 'ENERC' );
	$( "#yitem" ).val( 'ENERC' );

	$( "#zitem" ).val( 'ENERC' );
	$( "#zml" ).val( 0 );
	$( "#zrange" ).val( 0 );
};

// Dosplaying recipe by scatter plott
var resize3dp = function(){
	const plott_size = $( document.documentElement ).width();
	const frame_rate = $( "#area_size" ).val();

	window.chart_recipe3d.resize({
		height: plott_size * frame_rate,
		width: plott_size * frame_rate
	});

	const range = $( "#range" ).val();
	const type = $( "#type" ).val();
	const role = $( "#role" ).val();
	const tech = $( "#tech" ).val();
	const time = $( "#time" ).val();
	const cost = $( "#cost" ).val();

	const xitem = $( "#xitem" ).val();
	const yitem = $( "#yitem" ).val();
	const zitem = $( "#zitem" ).val();
	const zml = $( "#zml" ).val();
	const zrange = $( "#zrange" ).val();

	const area_size = $( "#area_size" ).val();
	const x_zoom = $( "#x_zoom" ).prop( "checked" );
	const y_log  = $( "#y_log" ).prop( "checked" ) ? 'log' : 'linear';
	postReq_recipe3ds( 'config', { range, type, role, tech, time, cost,
		xitem, yitem, zitem, zml, zrange, area_size, x_zoom, y_log }, data => {
//		$( "#L3" ).html( data );
	});

};

$( document ).ready( function(){
	recipe3dsPlottDraw();
});

</script>

JS

	puts js 
end

puts '(^q^)<br>' if @debug
