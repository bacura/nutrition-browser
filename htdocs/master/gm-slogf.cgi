#! /usr/bin/ruby
#encoding: utf-8
#Nutrition browser 2020 GM slogf viewer 0.00b (2023/07/22)

#==============================================================================
#STATIC
#==============================================================================
@debug = false
#script = File.basename( $0, '.cgi' )

#==============================================================================
#LIBRARY
#==============================================================================
require '../soul'

#==============================================================================
#DEFINITION
#==============================================================================

# Language pack
def language_pack( language )
	l = Hash.new

	#Japanese
	l['jp'] = {
		'user' 	=> "ユーザー",\
		'word' 	=> "ワード",\
		'code'	=> "code",\
		'date'	=> "日付",\
		'slogf_view' => "検索語ビューア"
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


#### GM check
if user.status < 8
	puts "GM error."
	exit
end


#### POST
command = @cgi['command']
if @debug
	puts "command:#{command}<br>\n"
	puts "<hr>\n"
end


if command == 'edit'
#	db.query( "UPDATE #{$MYSQL_TB_USER} SET;", true )
end


slogf_html = "<div class='row'>"
r = db.query( "SELECT * FROM #{$MYSQL_TB_SLOGF};", false )
if r.first
	slogf_html << "<table class='table-striped table-bordered'>"
	slogf_html << "<thead>"
	slogf_html << "<th>#{l['user']}</th>"
	slogf_html << "<th>#{l['word']}</th>"
	slogf_html << "<th>#{l['code']}</th>"
	slogf_html << "<th>#{l['date']}</th>"
	slogf_html << "</thead>"

	r.each do |e|
		if e['code'].to_i == 0 || e['code'].size >= 5
		slogf_html << "<tr>"
		slogf_html << "<td>#{e['user']}</td>"
		slogf_html << "<td>#{e['words']}</td>"
		slogf_html << "<td>#{e['code']}</td>"
		slogf_html << "<td>#{e['date']}</td>"
		slogf_html << "</tr>"
			end
	end
	slogf_html << "</table>"
else
	slogf_html << 'no slogf.'
end


html = <<-"HTML"
<div class='container-fluid'>
	<div class='row'>
		<div class='col'><h5>#{l['slogf_view']}: </h5></div>
	</div>
	#{slogf_html}
</div>


HTML

puts html
