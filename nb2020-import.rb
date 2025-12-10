#! /usr/bin/ruby
#encoding: utf-8
#Nutrition browser 2020 import 0.0.0 (2024/10/14)

#==============================================================================
#STATIC
#==============================================================================
@debug = false


#==============================================================================
#LIBRARY
#==============================================================================
require './nb2020-soul'

#==============================================================================
#DEFINITION
#==============================================================================


#==============================================================================
# Main
#==============================================================================

#### data loading
import_solid = []
txt_class = ''
line1_flag = true

opt = ARGV[0]
data_file = ARGV[1]
if ARGV[1] == nil
	data_file = opt 
	opt = 'ad'
end

if data_file == nil
	puts 'Nutrition browser 2020 import 0.0.0 (2024/10/14)'
	puts '[Usage]ruby nb2020-import.rb mode_option data'
	puts '[Mode option]'
	puts 'xx -> exchange'
	puts 'ow -> overwrite'
	puts 'ad -> add (default)'
	exit
end


File.open( data_file, 'r' ) do |f|
	f.each_line do |line|
		if line1_flag
			a = line.chomp.split( "\s" )
			if a[0] == 'NB2020' && /^\[\w+\]$/ =~ a[1] && a[2] == 'data'
				txt_class = a[1].sub( '[', '' ).sub( ']', '' )
				line1_flag = false
			else
				puts 'Incomplete data.'
				exit( 0 )
			end
		else
			import_solid << line.force_encoding( 'utf-8' ).chomp.split( "\t" )
		end
	end
end
puts "[#{txt_class}]"

if import_solid.size == 0
	puts 'Empty data.'
	exit
end

#### DB upadate
count = 0
case txt_class
when 'dic'
	#FG org_name alias user def_fn
	if import_solid[0].size == 5
		$DB.query( "DELETE FROM #{$MYSQL_TB_DIC};" ) if opt == 'xx'

		import_solid.each do |e|
			print "#{count}\r"

			begin
				res = $DB.query( "SELECT * FROM #{$MYSQL_TB_DIC} WHERE FG='#{e[0]}' AND org_name='#{e[1]}' AND alias='#{e[2]}';" )

				if res.first
					$DB.query( "UPDATE #{$MYSQL_TB_DIC} SET user='#{e[3]}', def_fn='#{e[4]}' WHERE FG='#{e[0]}'AND org_name='#{e[1]}' AND alias='#{e[2]}';" ) if opt == 'ow'
				else

					$DB.query( "INSERT INTO #{$MYSQL_TB_DIC} SET FG='#{e[0]}', org_name='#{e[1]}', alias='#{e[2]}', user='#{e[3]}', def_fn='#{e[4]}';" )
				end

			rescue
				puts "[ERROR]#{e}"
			end
			count += 1
		end
	else
		puts 'Incomplete dic data.'
	end
	puts "#{count} data have imported."

else
	puts 'Importable data list..'
	puts 'dic'
end

