from generators import ApacheGenerator, NginxGenerator
import argparse
import sys


HTTP_CONFIG = "http.yaml"


parser = argparse.ArgumentParser(description="Generate configs fast")
parser.add_argument("--apache", dest="generators", action="append_const", const="apache", help="Generate an Apache config from %s" % HTTP_CONFIG)
parser.add_argument("--nginx", dest="generators", action="append_const", const="nginx", help="Generate an Nginx config from %s" % HTTP_CONFIG)

args = parser.parse_args()

if not args.generators:
	parser.print_help()
	print "\nError: no generator specified."
	sys.exit(0)


if "apache" in args.generators:
	apache = ApacheGenerator(HTTP_CONFIG, "output/apache/")
	apache.generate()

if "nginx" in args.generators:
	nginx = NginxGenerator(HTTP_CONFIG, "output/nginx/")
	nginx.generate()

print "Configurations generated for %s" % args.generators
