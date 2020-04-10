#! /usr/bin/ruby
#encoding: utf-8
#Nutrition browser meta data viewer 0.00

#==============================================================================
#CHANGE LOG
#==============================================================================
#20180402, 0.00, start


#==============================================================================
#LIBRARY
#==============================================================================
require '/var/www/nb-soul.rb'


#==============================================================================
#STATIC
#==============================================================================
script = 'meta'
@debug = false


#==============================================================================
#DEFINITION
#==============================================================================


#==============================================================================
# Main
#==============================================================================
cgi = CGI.new

html_init( nil )

user = User.new( cgi )
user.debug if @debug
lp = user.language( script )


#### POSTデータの取得
command = cgi['command']
if @debug
	puts "command:#{command}<br>"
	puts "<hr>"
end


html = ''
case command

when 'food'
	fct_num = 0
	fctu_num = 0
	fctp_num = 0

	r = mariadb( "SELECT * FROM #{$MYSQL_TB_FCT};", false )
	fct_num = r.size

	r = mariadb( "SELECT * FROM #{$MYSQL_TB_FCTP};", false )

	r.each do |e|
		if /U/ =~ e['FN']
			fctu_num += 1
		elsif /P/ =~ e['FN']
			fctp_num += 1
		end
	end

	html = <<-"HTML"
<h5>#{lp[1]}</h5>
<table class="table">
	<thead>
		<tr>
			<th scope="col">#{lp[2]}</th>
			<th scope="col">#{lp[3]}</th>
		</tr>
	</thead>
	<tbody>
		<tr>
			<td>#{lp[4]}</td>
			<td>#{fct_num}</td>
		</tr>
		<tr>
			<td>#{lp[5]}</td>
			<td>#{fctu_num}</td>
		</tr>
		<tr>
			<td>#{lp[6]}</td>
			<td>#{fctp_num}</td>
		</tr>
	</tbody>
</table>
HTML

when 'user'
	r = mariadb( "SELECT * FROM #{$MYSQL_TB_USER};", false )
	cumulative_user_num = r.size

	r = mariadb( "SELECT * FROM #{$MYSQL_TB_USER} WHERE status=1;", false )
	general_user_num = r.size

	r = mariadb( "SELECT * FROM #{$MYSQL_TB_USER} WHERE status=2;", false )
	guild_member_num = r.size

	r = mariadb( "SELECT * FROM #{$MYSQL_TB_USER} WHERE status=4;", false )
	guild_moe_num = r.size

	r = mariadb( "SELECT * FROM #{$MYSQL_TB_USER} WHERE status=5;", false )
	guild_shun_num = r.size

	r = mariadb( "SELECT * FROM #{$MYSQL_TB_USER} WHERE status=6;", false )
	children_num = r.size

	r = mariadb( "SELECT * FROM #{$MYSQL_TB_USER} WHERE status=3 OR status=8 OR status=9;", false )
	admin_user_num = r.size

	html = <<-"HTML"
<h5>#{lp[7]}</h5>
<table class="table">
	<thead>
		<tr>
			<th scope="col">#{lp[8]}</th>
			<th scope="col">#{lp[9]}</th>
		</tr>
	</thead>
	<tbody>
		<tr>
			<td>#{lp[26]}</td>
			<td>#{cumulative_user_num - 1}</td>
		</tr>
		<tr>
			<td>#{lp[10]}</td>
			<td>#{general_user_num - 1}</td>
		</tr>
		<tr>
			<td>#{lp[11]}</td>
			<td>#{guild_member_num}</td>
		</tr>
		<tr>
			<td>#{lp[27]}</td>
			<td>#{guild_moe_num}</td>
		</tr>
		<tr>
			<td>#{lp[28]}</td>
			<td>#{guild_shun_num}</td>
		</tr>
		<tr>
			<td>#{lp[12]}</td>
			<td>#{admin_user_num}</td>
		</tr>
		<tr>
			<td>#{lp[29]}</td>
			<td>#{children_num}</td>
		</tr>
	</tbody>
</table>
HTML

when 'recipe'
	r = mariadb( "SELECT * FROM #{$MYSQL_TB_RECIPE};", false )
	recipe_total_num = r.size

	r = mariadb( "SELECT * FROM #{$MYSQL_TB_RECIPE} WHERE role!=100;", false )
	recipe_real_num = r.size

	r = mariadb( "SELECT * FROM #{$MYSQL_TB_RECIPE} WHERE public=1;", false )
	recipe_public_num = r.size

	r = mariadb( "SELECT * FROM #{$MYSQL_TB_RECIPE} WHERE public=1 AND role!=100;", false )
	recipe_real_public_num = r.size

	r = mariadb( "SELECT * FROM #{$MYSQL_TB_RECIPE} WHERE user='#{user.name}';", false )
	recipe_user_num = r.size

	r = mariadb( "SELECT * FROM #{$MYSQL_TB_RECIPE} WHERE user='#{user.name}' and public=1;", false )
	recipe_user_public_num = r.size

	html = <<-"HTML"
<h5>#{lp[13]}</h5>
<table class="table">
	<thead>
		<tr>
			<th scope="col">#{lp[14]}</th>
			<th scope="col">#{lp[15]}</th>
		</tr>
	</thead>
	<tbody>
		<tr>
			<td>#{lp[16]}</td>
			<td>#{recipe_total_num}</td>
		</tr>
		<tr>
			<td>#{lp[30]}</td>
			<td>#{recipe_real_num}</td>
		</tr>
		<tr>
			<td>#{lp[17]}</td>
			<td>#{recipe_public_num}</td>
		</tr>
		<tr>
			<td>#{lp[31]}</td>
			<td>#{recipe_real_public_num}</td>
		</tr>
		<tr>
			<td>#{user.name}#{lp[18]}</td>
			<td>#{recipe_user_num}</td>
		</tr>
		<tr>
			<td>#{user.name}#{lp[19]}</td>
			<td>#{recipe_user_public_num}</td>
		</tr>
	</tbody>
</table>
HTML

when 'menu'
	r = mariadb( "SELECT * FROM #{$MYSQL_TB_MENU};", false )
	menu_total_num = r.size

	r = mariadb( "SELECT * FROM #{$MYSQL_TB_MENU} WHERE public=1;", false )
	menu_public_num = r.size

	html = <<-"HTML"
<h5>#{lp[20]}</h5>
<table class="table">
	<thead>
		<tr>
			<th scope="col">#{lp[21]}</th>
			<th scope="col">#{lp[22]}</th>
		</tr>
	</thead>
	<tbody>
		<tr>
			<td>#{lp[23]}</td>
			<td>#{menu_total_num}</td>
		</tr>
		<tr>
			<td>#{lp[24]}</td>
			<td>#{menu_public_num}</td>
		</tr>
	</tbody>
</table>
HTML

else
	html = "#{lp[25]}"
end

puts html
