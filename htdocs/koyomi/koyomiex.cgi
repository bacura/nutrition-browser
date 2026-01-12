#! /usr/bin/ruby
#encoding: utf-8
#Nutrition browser 2020 koyomi extra 0.2.4 (2026/01/12)


#==============================================================================
#LIBRARY
#==============================================================================
require '../soul'
require '../brain'
require '../body'

#==============================================================================
#STATIC
#==============================================================================
@debug = false
myself = $KOYOMI_PATH + "/" + File.basename( __FILE__ )

#==============================================================================
#DEFINITION
#==============================================================================

# Language pack
def language_pack( language )
	l = Hash.new

	#Japanese
	l['ja'] = {
		koyomi: "こよみ:拡張",
		sun: 	"日",
		mon: 	"月",
		tue: 	"火",
		wed: 	"水",
		thu: 	"木",
		fri: 	"金",
		sat: 	"土",
		year: 	"年",
		month: 	"月",
		day: 	"日",
		basic: 	"基本",
		geo:	"<img src='bootstrap-dist/icons/geo.svg' style='height:2em; width:2em;'>",
		table:	"<img src='bootstrap-dist/icons/table.svg' style='height:1.5em; width:1.5em;'>",
		tsv:	"TSV<img src='bootstrap-dist/icons/download.svg' style='height:1.5em; width:1.5em;'>"
	}

	return l[language]
end

#==============================================================================
# Main
#==============================================================================
html_init( nil )

user = User.new( @cgi )
user.debug if @debug
l = language_pack( user.language)
db = Db.new( user, @debug, false )

html = []

puts 'CHECK membership<br>' if @debug
if user.status < 3
	puts "Guild member error."
	exit
end


puts 'GET POST<br>' if @debug
command = @cgi['command']
yyyy = @cgi['yyyy'].to_i
mm = @cgi['mm'].to_i
yyyy_mm = @cgi['yyyy_mm']
dd = @cgi['dd'].to_i
unless yyyy_mm == ''
	a = yyyy_mm.split( '-' )
	yyyy = a[0].to_i
	mm = a[1].to_i
end
dd = 1 if dd == 0
kex_key = @cgi['kex_key']
cell = @cgi['cell']
if @debug
	puts "command:#{command}<br>\n"
	puts "yyyy:#{yyyy}<br>\n"
	puts "mm:#{mm}<br>\n"
	puts "dd:#{dd}<br>\n"
	puts "kex_key:#{kex_key}<br>\n"
	puts "cell:#{cell}<br>\n"
	puts "<hr>\n"
end


puts "INITIALIZE Date<br>" if @debug
date = Date.today
date = Date.new( yyyy, mm, dd ) unless yyyy == 0
if yyyy == 0
 	yyyy = date.year
	mm = date.month
	dd = date.day
end
puts "date:#{date.to_time}<br>" if @debug

puts "INITIALIZE calendar<br>" if @debug
calendar = Calendar.new( user, yyyy, mm, dd )
calendar_td = Calendar.new( user, 0, 0, 0 )
calendar.debug if @debug
sql_ymd = "#{calendar.yyyy}-#{calendar.mm}-#{calendar.dd}"
sql_ym = "#{calendar.yyyy}-#{calendar.mm}"


puts "LOAD config<br>" if @debug
start = Time.new.year
kexu = Hash.new
kexa = Hash.new

res = db.query( "SELECT koyomi FROM #{$TB_CFG} WHERE user=?", false, [user.name] )&.first
if res
	unless res['koyomi'].to_s.empty?
		begin
			koyomi = JSON.parse( res['koyomi'] )
    	rescue JSON::ParserError => e
      		puts "J(x_x)P: #{e.message}<br>"
      		koyomi = {}
    	end			
		start = koyomi['start'].to_i unless koyomi['start'].nil?
		kexu = koyomi['kexu'] unless koyomi['kexu'].nil?
		kexa = koyomi['kexa'] unless koyomi['kexa'].nil?
	end
end


puts "HTML Header<br>" if @debug
th_html = '<thead><tr>'
th_html << "<th align='center'></th>"
kexu.each do |k, v|
	th_html << "<th align='center'>#{k} (#{v})</th>" if kexa[k] == '1'
end
th_html << '</tr></thead>'


puts "LOAD date cell<br>" if @debug
cells_day = []
r = db.query( "SELECT * FROM #{$TB_KOYOMIEX} WHERE user=? AND ( date BETWEEN ? AND ? )", false, [user.name, "#{sql_ym}-1", "#{sql_ym}-#{calendar.ddl}"] )
r.each do |e|
	unless e['cell'].to_s.empty?
		cells_day[e['date'].day] = JSON.parse( e['cell'] )
	end
end


if command == 'update'
	puts "UPDATE cell<br>" if @debug
	unless cells_day[dd].to_s.empty?
		kexc = Hash.new
		kexu.each do |k, |
			if k == kex_key
				kexc[k] = cell
			else
				kexc[k] = ''
			end
			cells_day[dd] = kexc
		end
	else
		cells_day[dd] = Hash.new
		cells_day[dd][kex_key] = cell
	end
end


puts "HTML Cell<br>" if @debug
week_count = calendar.wf
date_html = ''
weeks = [l[:sun], l[:mon], l[:tue], l[:wed], l[:thu], l[:fri], l[:sat]]
1.upto( calendar.ddl ) do |c|
	style = ''
	style = "style='color:red;'" if week_count == 0
	date_html << "<tr id='day#{c}'>"
	date_html << "<td #{style}><span>#{c}</span> (#{weeks[week_count]})</td>"
	kexa.each do |k, v|
		if cells_day[c] == nil
			date_html << "<td><input type='text' id='#{k}#{c}' value='' onChange=\"updateKoyomiex( '#{k}', '#{c}' )\"></td>" if v == '1'
		else
			date_html << "<td><input type='text' id='#{k}#{c}' value='#{cells_day[c][k]}' onChange=\"updateKoyomiex( '#{k}', '#{c}' )\"></td>" if v == '1'
		end
	end

	date_html << "</tr>"
	week_count += 1
	week_count = 0 if week_count > 6
end


####
####
puts "HTML10<br>" if @debug
html[10] = <<~"HTML10"
<div class='container-fluid'>
	<div class='row'>
		<div class='col-2'><h5>#{l[:koyomi]}</h5></div>
		<div class='col-2 form-inline'>
			<input type='month' class='form-control form-control-sm' id='yyyy_mm' min='#{calendar.yyyyf}-01' max='#{calendar.yyyy + 2}-01' value='#{calendar.yyyy}-#{calendar.mms}' onChange="changeKoyomiex()">
		</div>
		<div class='col-4'>
			<form method='post' enctype='multipart/form-data' id='table_form'>
			<div class='input-group input-group-sm'>
				<label class="input-group-text">#{l[:table]}</label>
				<input type='file' class='form-control' name='extable' onchange="importkoyomiex()">
			</div>
			</form>
		</div>
		<div align='center' class='col-3 joystic_koyomi' onclick="window.location.href='#day#{date.day}';">#{l[:geo]}</div>
		<div class='col-1'>
			<a href='koyomi/koyomiex-txt.cgi?' download='koyomiex-#{user.name}-#{sql_ym}.txt'>#{l[:tsv]}</a>
		</div>
	</div>
	<div class='row'>
		<div class='col'></div>
	</div>
	<br>

	<table class="table table-sm table-hover">
	#{th_html}
	#{date_html}
	</table>

HTML10
####
####

puts html.join

#==============================================================================
# POST PROCESS
#==============================================================================
if command == 'update'
	puts "UPDATE cell<br>" if @debug
	cell_ = JSON.generate( cells_day[dd] )
	res = db.query( "SELECT user FROM #{$TB_KOYOMIEX} WHERE user=? AND date=?", false, [user.name, sql_ymd] )&.first
	if res
		db.query( "UPDATE #{$TB_KOYOMIEX} SET cell=? WHERE user=? AND date=?", true, [cell_, user.name, sql_ymd] )
	else
		db.query( "INSERT INTO #{$TB_KOYOMIEX} SET cell=?, user=?, date=?", true, [cell_, user.name, sql_ymd]  )
	end
end


if command == 'init'
	puts "CLEAN empty cell<br>" if @debug
#	db.query( "DELETE FROM #{$TB_KOYOMIEX} WHERE cell='' OR cell IS NULL;", false )
end

#==============================================================================
#FRONT SCRIPT
#==============================================================================
if command == 'init'
	js = <<~"JS"
<script type='text/javascript'>

// Koyomi EX change
var changeKoyomiex = () => {
	const yyyy_mm = document.getElementById( "yyyy_mm" ).value;

	postLayer( '#{myself}', 'init', true, 'L1', { yyyy_mm });
};


// Updating Koyomiex cell
var updateKoyomiex = ( kex_key, dd ) => {
	const yyyy_mm = document.getElementById( "yyyy_mm" ).value;
	const cell = document.getElementById( kex_key + dd ).value;

	postLayer( '#{myself}', 'update', true, 'L1', { yyyy_mm, dd, kex_key, cell });
};

</script>

JS

	puts js
end

puts '<br>(^q^)' if @debug
