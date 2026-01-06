#! /usr/bin/ruby
#encoding: utf-8
#Nutrition browser 2020 export 0.1.0 (2026/01/04)

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

case ARGV[0]
when 'unit'
	export = ''
	puts "SELECT * FROM #{$TB_EXT};"
	r = $DB.query( "SELECT * FROM #{$TB_EXT};" )
	r.each do |e| export << "#{e['FN']}\t#{e['unit']}\n" end
	puts "NB2020 [unit] data #{@date}\n"
	puts export.force_encoding( 'UTF-8' )

when 'gycv'
	export = ''
	r = $DB.query( "SELECT * FROM #{$TB_EXT} WHERE gycv=1;" )
	r.each do |e| export << "#{e['FN']}\n" end
	puts "NB2020 [gycv] data #{@date}\n"
	puts export.force_encoding( 'UTF-8' )

when 'shun'
	export = ''
	r = $DB.query( "SELECT * FROM #{$TB_EXT};" )
	r.each do |e| export << "#{e['FN']}\t#{e['shun1s']}\t#{e['shun1e']}\t#{e['shun2s']}\t#{e['shun2e']}\n" end
	puts "NB2020 [shun] data\n"
	puts export.force_encoding( 'UTF-8' )

when 'allergen'
	export = ''
	r = $DB.query( "SELECT * FROM #{$TB_EXT};" )
	r.each do |e| export << "#{e['FN']}\t#{e['allergen1']}\t#{e['allergen2']}\n" end
	puts "NB2020 [allergen] data #{@date}\n"
	puts export.force_encoding( 'UTF-8' )

when 'dic'
	export = ''
	r = $DB.query( "SELECT * FROM #{$TB_DIC} ORDER BY FG, org_name;" )
	r.each do |e|
		export << "#{e['FG']}\t#{e['org_name']}\t#{e['alias'].gsub( '<br>', ',' )}\t#{e['user']}\t#{e['def_fn']}\n" unless e['org_name'].empty?
	end
	puts "NB2020 [dic] data #{@date}\n"
	puts export.force_encoding( 'UTF-8' )

when 'memory'
	export = ''
	r = $DB.query( "SELECT * FROM #{$TB_MEMORY};" )
	r.each do |e| export << "#{e['user']}\t#{e['category']}\t#{e['pointer']}\t#{e['memory']}\t#{e['rank']}\t#{e['total_rank']}\t#{e['count']}t#{e['know']}\t#{e['date']}\n" end
	puts "NB2020 [memory] data #{@date}\n"
	puts export.force_encoding( 'UTF-8' )

when 'fctp'
	export = ''
	r = $DB.query( "SELECT * FROM #{$TB_FCTP} WHERE user='#{ARGV[1]}';" )
	r.each do |e|
		export << "#{e['user']}"
		@fct_item.each do |item| export << "\t#{e[item]}" end
		export << "\n"
	end
	puts "NB2020 [fctp] data (#{ARGV[1]}) #{@date}\n"
	items = "user"
	@fct_item.each do |item| items << "\t#{item}" end
	puts items + "\n"
	puts export.force_encoding( 'UTF-8' )

when 'tagp'
	export = ''
	r = $DB.query( "SELECT * FROM #{$TB_TAG} INNER JOIN #{$TB_FCTP} ON #{$TB_TAG}.FN = #{$TB_FCTP}.FN WHERE #{$TB_TAG}.user='#{ARGV[1]}';" )
	r.each do |e| export << "#{e['FG']}\t#{e['FN']}\t#{e['SID']}\t#{e['SN']}\t#{e['user']}\t#{e['name']}\t#{e['class1']}\t#{e['class2']}\t#{e['class3']}\t#{e['tag1']}\t#{e['tag2']}\t#{e['tag3']}\t#{e['tag4']}\t#{e['tag5']}\t#{e['status']}\n" end
	puts "NB2020 [tagp] data (#{ARGV[1]}) #{@date}\n"
	puts "FG\tFN\tSID\tSN\tuser\tname\tclass1\tclass2\tclass3\ttag1\ttag2\ttag3\ttag4\ttag5\tstatus\n"
	puts export.force_encoding( 'UTF-8' )

when 'extp'
	export = ''
	r = $DB.query( "SELECT * FROM #{$TB_EXT} INNER JOIN #{$TB_FCTP} ON #{$TB_EXT}.FN = #{$TB_FCTP}.FN WHERE #{$TB_EXT}.user='#{ARGV[1]}';" )
	r.each do |e| export << "#{e['FN']}\t#{e['user']}\t#{e['gycv']}\t#{e['allergen1']}\t#{e['allergen2']}\t#{e['unit']}\t#{e['color1']}\t#{e['color2']}\t#{e['color1h']}\t#{e['color2h']}\t#{e['shun1s']}\t#{e['shun1e']}\t#{e['shun2s']}\t#{e['shun2e']}\n" end
	puts "NB2020 [extp] data (#{ARGV[1]}) #{@date}\n"
	puts "FN\tuser\tgycv\tallergen1\tallergen2\tunit\tcolor1\tcolor2\tcolor1h\tcolor2h\tshun1s\tshun1e\tshun2s\tshun2e\n"
	puts export.force_encoding( 'UTF-8' )

else
	puts 'Nutrition browser 2020 export 0.0.2 (2024/10/14)'
	puts '[Usage]ruby nb2020-export.rb Exportable data [user]> nb2020-dic.txt'
	puts 'Exportable data list..'
	puts 'unit'
	puts 'gycv'
	puts 'shun'
	puts 'allergen'
	puts 'dic'
	puts 'memory'
	puts 'fctp'
	puts 'tagp'
	puts 'extp'
end
