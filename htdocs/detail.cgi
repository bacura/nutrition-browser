#! /usr/bin/ruby
#encoding: utf-8
#Nutrition browser 2020 detail viewer 0.1.7 (2026/01/21)

#==============================================================================
# LIBRARY
#==============================================================================
require './soul'
require './brain'

#==============================================================================
# STATIC
#==============================================================================
@debug = false
sn_max = 2538
myself = File.basename( __FILE__ )

#==============================================================================
# DEFINITION
#==============================================================================

# Language pack
def language_pack( language )
	l = Hash.new

	#Japanese
	l['ja'] = {
		login:    "ログインが必要",
		aliase:   "別名",
		request:  "リクエスト",
		fract:    "端数",
		food_no:  "食品番号",
		sid:      "索引番号",
		round:    "四捨五入",
		ceil:     "切り上げ",
		floor:    "切り捨て",
		volume:   "量",
		skey:     "検索キー",
		notice:   "備考：",
		calendar: "暦+",
		cboard:   "<img src='bootstrap-dist/icons/card-text.svg' style='height:2em; width:2em;'>",
		rev:      "<img src='bootstrap-dist/icons/caret-left.svg' style='height:1.5em; width:1.5em;'>",
		fwd:      "<img src='bootstrap-dist/icons/caret-right.svg' style='height:1.5em; width:1.5em;'>",
		downlord: "<img src='bootstrap-dist/icons/filetype-txt.svg' style='height:2em; width:2em;'>",
		return:   "<img src='bootstrap-dist/icons/signpost-r.svg' style='height:2em; width:2em;'>"
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

puts 'POST<br>' if @debug
command = @cgi['command']
frct_mode = @cgi['frct_mode']
food_weight = @cgi['food_weight']
food_no = @cgi['food_no']
selectu = @cgi['selectu'].to_s
if @debug
	puts "command: #{command}<br>"
	puts "frct_mode: #{frct_mode}<br>"
	puts "food_weight: #{food_weight}<br>"
	puts "food_no: #{food_no}<br>"
	puts "selectu: #{selectu}<br>"
	puts "<hr>"
end


puts 'Unit process<br>' if @debug
unit_set = []
unit_select = []
selectu = 'g' if selectu.empty?
uk = BigDecimal( '1' )
res = db.query( "SELECT unit FROM #{$TB_EXT} WHERE FN=?", false, [food_no] )&.first
if res
	unith = JSON.parse( res['unit'] )
	unith.each do |k, v|
		next if k == 'note'

		unit_set << k
		if k == selectu
			unit_select << 'SELECTED'
			uk = BigDecimal( v.to_s )
		else
			unit_select << ''
		end
	end
end


puts 'Weight process<br>' if @debug
food_volume = BigDecimal( food_weight_check( food_weight ).first )
food_weight = food_volume * uk


puts 'Load FCT<br>' if @debug
fct_opt = Hash.new
res = db.query( "SELECT * FROM #{$TB_FCT} WHERE FN=?", false, [food_no] )&.first
if res
	sid = res['SID']
	food_no = res['FN']
	@fct_item.each do |e| fct_opt[e] = num_opt( res[e], food_weight, frct_mode, @fct_frct[e] ) end
end

puts 'Aliase process<br>' if @debug
search_key = ''
r = db.query( "SELECT alias FROM #{$TB_DIC} WHERE org_name=(SELECT name FROM #{$TB_TAG} WHERE FN=?)", false, [food_no] )
r.each do |e| search_key << "#{e['alias']}," end
search_key.chop!

alias_button = ''
#if user.status > 0
#	alias_button << '<div class="input-group input-group-sm">'
#	alias_button << "<label class='input-group-text' for='alias'>#{l[:aliase]}</label>"
#	alias_button <<	'<input type="text" class="form-control" id="alias">'
#	alias_button <<	"<div class='input-group-prepend'><button class='btn btn-outline-primary' type='button' onclick=\"aliasRequest( '#{food_no}' )\">#{l[:request]}</button></div>"
#	alias_button << '</div>'
#end


puts 'Search index<br>' if @debug
res = db.query( "SELECT SN FROM #{$TB_TAG} WHERE FN=?", false, [food_no] )&.first
sn = res['SN'].to_i

sn_rev = sn - 1
sn_rev = sn_max if sn_rev < 1
res = db.query( "SELECT FN FROM #{$TB_TAG} WHERE SN=?", false, [sn_rev] )&.first
fn_rev = res['FN']

sn_fwd = sn + 1
sn_fwd = 1 if sn_fwd > sn_max
res = db.query( "SELECT FN FROM #{$TB_TAG} WHERE SN=?", false, [sn_fwd] )&.first
fn_fwd = res['FN']


puts 'FCT table HTML<br>' if @debug
energy_html = '<table class="table table-sm" width="100%">'
energy_html << "<tr>"
@fct_rew.each do |e| energy_html << "<tr><td>#{@fct_name[e]}</td><td align='right'>#{fct_opt[e]} #{@fct_unit[e]}</td></tr>" end
energy_html << '</table>'

pf_html = '<table class="table table-sm" width="100%">'
@fct_pf.each do |e| pf_html << "<tr><td>#{@fct_name[e]}</td><td align='right'>#{fct_opt[e]} #{@fct_unit[e]}</td></tr>" end
pf_html << '</table>'

cho_html = '<table class="table table-sm" width="100%">'
@fct_cho.each do |e| cho_html << "<tr><td>#{@fct_name[e]}</td><td align='right'>#{fct_opt[e]} #{@fct_unit[e]}</td></tr>" end
cho_html << '</table>'

mineral_html = '<table class="table table-sm" width="100%">'
@fct_m.each do |e| mineral_html << "<tr><td>#{@fct_name[e]}</td><td align='right'>#{fct_opt[e]} #{@fct_unit[e]}</td></tr>" end
mineral_html << '</table>'

fsv_html = '<table class="table table-sm" width="100%">'
@fct_fsv.each do |e| fsv_html << "<tr><td>#{@fct_name[e]}</td><td align='right'>#{fct_opt[e]} #{@fct_unit[e]}</td></tr>" end
fsv_html << '</table>'

wsv_html = '<table class="table table-sm" width="100%">'
@fct_wsv.each do |e| wsv_html << "<tr><td>#{@fct_name[e]}</td><td align='right'>#{fct_opt[e]} #{@fct_unit[e]}</td></tr>" end
wsv_html << "<tr><td></td><td></td></tr>"
@fct_as.each do |e| wsv_html << "<tr><td>#{@fct_name[e]}</td><td align='right'>#{fct_opt[e]} #{@fct_unit[e]}</td></tr>" end
wsv_html << '</table>'


puts 'Volume input HTML<br>' if @debug
volume_html = <<~HTML
	<div class='input-group input-group-sm'>
		<label class='input-group-text' for='detail_volume'>#{l[:volume]}</label>
		<input type='text' id='detail_volume' value='#{food_volume.to_f}' class='form-control' onchange="detailWeight( '#{food_no}' )">
		<select id='detail_unit' class='form-select form-select-sm' onchange="detailWeight( '#{food_no}' )">
		#{unit_set.each_with_index.map { |u, i| "<option value='#{u}' #{unit_select[i]}>#{u}</option>" }.join}
		</select>
	</div>
HTML


puts 'Fract input HTML<br>' if @debug
fract_html = <<~HTML
	<div class="input-group input-group-sm">
		<label class='input-group-text' for='detail_fraction'>#{l[:fract]}</label>
		<select class='form-select form-select-sm' id='detail_fraction' onchange="detailWeight( '#{food_no}' )">
			<option value='1' #{$SELECT[frct_mode == 1]}>#{l[:round]}</option>
			<option value='2' #{$SELECT[frct_mode == 2]}>#{l[:ceil]}</option>
			<option value='3' #{$SELECT[frct_mode == 3]}>#{l[:floor]}</option>
		</select>
	</div>
HTML


puts 'HTML<br>' if @debug
html = <<-"HTML"
<div class='container-fluid'>
	<div class="row">
		<div class="col-2">
			<span class='h6'>#{l[:food_no]}：#{food_no}</span><br>
			<span onclick="detailWeight( '#{fn_rev}' )">#{l[:rev]}</span>
			#{l[:sid]}：#{sid}</span>
			<span onclick="detailWeight( '#{fn_fwd}' )">#{l[:fwd]}</span>
		</div>
		<div class="col"><h6>#{fct_opt['Tagnames']}</h6></div>
	  	<div class="col-2"><h6>#{food_volume.to_f} #{selectu}<br>#{food_weight.to_f} g</h6></div>
		<div align='center' class='col joystic_koyomi' onclick="detailReturn()">#{l[:return]}</div>

	  </div>
	</div>
	<br>
	<div class="row">
		<div class="col">
			#{volume_html}
		</div>
		<div class="col">
			#{fract_html}
		</div>
		<div class="col" align="right">
			<a href='plain-txt.cgi?food_no=#{food_no}&food_weight=#{food_weight}&frct_mode=#{frct_mode}&lg=#{user.language}' download='detail_#{fct_opt['FN']}.txt'><span>#{l[:downlord]}</span></a>
		</div>
	</div>
</div>
<br>

<div class='container-fluid'>
	<div class="row">
		<div class="col">
		#{energy_html}
		<div class='notice'>
			#{l[:notice]}<br>
			#{fct_opt['Notice']}
		</div>
		</div>

		<div class="col">
			#{pf_html}
		</div>

		<div class="col">
			#{cho_html}
		</div>
	</div>

	<div class="row">
		<div class="col">
			#{mineral_html}
		</div>

		<div class="col">
			#{fsv_html}
		</div>

		<div class="col-4">
			#{wsv_html}
		</div>
	</div>
</div>

<div class="row">
	<div class="col-8">
		#{l[:aliase]}：#{search_key}
	</div>
	<div class="col-4">
		#{alias_button}
	</div>
</div>
HTML
puts html


#==============================================================================
# POST PROCESS
#==============================================================================
puts 'Adding History<br>' if @debug
add_his( user, food_no )


#==============================================================================
# FRONT SCRIPT START
#==============================================================================

if command == 'init'
	js = <<-"JS"
<script type='text/javascript'>

//
var detailWeight = ( food_no ) => {
	const frct_mode = document.getElementById( 'detail_fraction' ).value;
	const food_weight = document.getElementById( 'detail_volume' ).value;
	const selectu = document.getElementById( 'detail_unit' ).value;

	postLayer( '#{myself}', 'weight', true, 'LF', { food_no, frct_mode, food_weight, selectu });
};

//
var detailReturn = () => {
	pullBW();
	displayBW();
};

</script>

JS
	puts js
end
