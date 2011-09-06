#!/usr/bin/env python
import cloudfiles, sys, os, getopt, glob

VERSION = '0.1'

def usage():
	print ''
	print 'Usage: %s [OPTION]... FILE...' % (os.path.basename(sys.argv[0]))
	print 'Uploads the specified files to a Rackspace CloudFiles account. The container'
	print 'will be created if necessary, and existing files will be overwritten.'
	print ''
	print '  -u, --username    your RackspaceCloud API username'
	print '  -k, --key         your RackspaceCloud API key'
	print '  -c, --container   the destination container name'
	print '  -s, --servicenet  set this if you\'re running in a CloudServer so it will use'
	print '                    the local network'
	print '  -d, --datacentre  specifies which data centre you\'re in, "us" or "uk"'
	print '                    if ommitted then "us" will be tried first then "uk"'
	print '  -q, --quiet       suppress all output except error messages'
	print ''
	print 'The username, key and container options are required.'
	print ''
	print 'This is v%s. Latest, bugs, etc: https://github.com/3ft9/CloudFiles-Uploader' % (VERSION)
	print ''

def upload_files(username, key, service_net, auth_url, container_name, files, prefix, quiet):
	try:
		# Attempt a connection
		conn = cloudfiles.get_connection(username = username, api_key = key, servicenet = service_net, authurl = auth_url)
	except cloudfiles.errors.AuthenticationFailed:
		try:
			# Switch to the other authurl and try again
			if auth_url == cloudfiles.us_authurl:
				auth_url = cloudfiles.uk_authurl
			else:
				auth_url = cloudfiles.us_authurl
			conn = cloudfiles.get_connection(username = username, api_key = key, servicenet = service_net, authurl = auth_url)
		except cloudfiles.errors.AuthenticationFailed:
			# Still didn't work
			sys.stderr.write('Authentication failed!\n')
			return
	except:
		sys.stderr.write('API connection failed!\n')
		return

	try:
		cont = conn.get_container(container_name)
	except cloudfiles.errors.NoSuchContainer:
		cont = conn.create_container(container_name)
	except:
		sys.stderr.write('Failed to create a container called "%s"\n' % (container_name))
	else:
		while len(files) > 0:
			f = files.pop(0)
			if os.path.isfile(f):
				try:
					if not quiet:
						sys.stdout.write('Uploading "%s"...\n' % (f))
					obj = cont.create_object('%s%s' % (prefix, f))
					obj.load_from_filename(f)
				except:
					sys.stderr.write('  Upload of "%s" failed!\n' % (f))
			elif f not in ('.', '..'):
				for filename in glob.glob("%s/*" % (f)):
					files.append(filename)

def main(argv):
	try:
		opts, files = getopt.getopt(argv, "hu:k:sd:c:p:q", ["help", "username=", "key=", "servicenet", "datacentre=", "container=", "prefix=", "quiet"])
	except getopt.GetoptError:
		usage()
		sys.exit(2)

	# Defaults
	username = False
	key = False
	container_name = False
	service_net = False
	auth_url = cloudfiles.us_authurl
	prefix = ""
	quiet = False

	for opt, arg in opts:
		if opt in ("-h", "--help"):
			usage()
			sys.exit()                  
		elif opt in ("-u", "--username"):
			username = arg
		elif opt in ("-k", "--key"):
			key = arg
		elif opt in ("-s", "--servicenet"):
			service_net = True
		elif opt in ("-p", "--prefix"):
			prefix = arg
		elif opt in ("-d", "--datacentre"):
			if arg == 'uk':
				auth_url = cloudfiles.uk_authurl
			elif arg == 'us':
				auth_url = cloudfiles.us_authurl
		elif opt in ("-c", "--container"):
			container_name = arg
		elif opt in ("-q", "--quiet"):
			quiet = True

	if username == False or key == False or container_name == False or len(files) == 0:
		usage()
	else:
		upload_files(username, key, service_net, auth_url, container_name, files, prefix, quiet)

if __name__ == "__main__":
    main(sys.argv[1:])
