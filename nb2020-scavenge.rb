#! /usr/bin/ruby
#encoding: utf-8
#Nutrition browser 2020 db scavenge 0.0.0 (2026/01/25)

ENV['REQUEST_METHOD'] = 'GET'
ENV['GATEWAY_INTERFACE'] = 'CGI/1.1'
#==============================================================================
#LIBRARY
#==============================================================================
require './nb2020-soul'

#==============================================================================
#STATIC
#==============================================================================
db = Mysql2::Client.new(:host => "#{$MYSQL_HOST}", :username => "#{$MYSQL_USER}", :password => "#{$MYSQL_PW}", :database => "#{$MYSQL_DB}", :encoding => "utf8" )


#==============================================================================
#DEFINITION
#==============================================================================

def fctp( db )
	print "[fctp]\n"
	r = db.query( "SELECT * FROM #{$TB_FCTP};" )
	r.each do |e|
		rr = db.query( "SELECT * from #{$TB_TAG} WHERE FN='#{e['FN']}' AND user='#{e['user']}';" )&.first
		unless rr
			print "fctp:#{e['FN']}-#{e['user']}\n"
			db.query( "DELETE FROM #{$TB_FCTP} WHERE FN='#{e['FN']}' AND user='#{e['user']}';" )
		end
	end
end

def tag( db )
	print "[tag]\n"
	r = db.query( "SELECT * FROM #{$TB_TAG};" )
	r.each do |e|
		if /P|U|C/ =~ e['FN']
			rr = db.query( "SELECT * from #{$TB_FCTP} WHERE FN='#{e['FN']}' AND user='#{e['user']}';" )&.first
		else
			rr = db.query( "SELECT * from #{$TB_FCT} WHERE FN='#{e['FN']}';" )&.first
		end

		unless rr
			print "tag:#{e['FN']}-#{e['user']}\n"
			db.query( "DELETE FROM #{$TB_TAG} WHERE FN='#{e['FN']}' AND user='#{e['user']}';" )
		end
	end
end

def ext( db )
	print "[ext]\n"
	r = db.query( "SELECT * FROM #{$TB_EXT};" )
	r.each do |e|
		rr = db.query( "SELECT * from #{$TB_TAG} WHERE FN='#{e['FN']}' AND user='#{e['user']}';" )&.first
		unless rr
			if e['user'].to_s != ''
				print "ext:#{e['FN']}-#{e['user']}\n"
				db.query( "DELETE FROM #{$TB_EXT} WHERE FN='#{e['FN']}' AND user='#{e['user']}';" )
			end
		end
	end
end


#==============================================================================
# Main
#==============================================================================

tag( db )
ext( db )
fctp( db )

