#! /usr/bin/ruby
#encoding: utf-8
#Nutrition browser 2020 db scavenge 0.00b


#==============================================================================
#LIBRARY
#==============================================================================
require './nb2020-soul_'


#==============================================================================
#STATIC
#==============================================================================


#==============================================================================
#DEFINITION
#==============================================================================


#==============================================================================
# Main
#==============================================================================

#### tag
r = mdb( "SELECT FN FROM #{$MYSQL_TB_TAG};", false, false )
r.each do |e|
	living_flag = false
	rr = mdb( "SELECT FN from #{$MYSQL_TB_FCT} WHERE FN='#{e['FN']}';", false, false )
	living_flag = true if rr.first

	rr = mdb( "SELECT FN from #{$MYSQL_TB_FCTP} WHERE FN='#{e['FN']}';", false, false )
	living_flag = true if rr.first

	unless living_flag
		puts e['FN']
		mdb( "DELETE FROM #{$MYSQL_TB_TAG} WHERE FN='#{e['FN']}';", false, false )
	end
end


#### extag
r = mdb( "SELECT FN FROM #{$MYSQL_TB_EXT};", false, false )
r.each do |e|
	living_flag = false
	rr = mdb( "SELECT FN from #{$MYSQL_TB_FCT} WHERE FN='#{e['FN']}';", false, false )
	living_flag = true if rr.first

	rr = mdb( "SELECT FN from #{$MYSQL_TB_FCTP} WHERE FN='#{e['FN']}';", false, false )
	living_flag = true if rr.first

	unless living_flag
		puts e['FN']
		mdb( "DELETE FROM #{$MYSQL_TB_EXT} WHERE FN='#{e['FN']}';", false, false )
	end
end
