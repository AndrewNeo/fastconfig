import copy
from generator import Generator

class NginxGenerator(Generator):

    def generate_templates(self, jinja):
        structure = self.map_structure()
        template_map = {
            "http": jinja.get_template("nginx.conf")
        }

        for domain, contents in structure.iteritems():
            f = open(self.output_dir + "/" + domain + ".conf", "w")
            f.write("# Autogenerated by fastconfig\n")
            f.write("# Configuration for " + domain)

            for site in contents:
                f.write("\n" + template_map["http"].render(site))

            f.close()


    def map_structure(self):
        output = {}

        for domain, dval in self.structure["sites"].iteritems():
            output[domain] = [];

            for val in dval["subdomains"]:
                subdomain = val["name"]
                site = {"webmaster": dval["webmaster"], "domain_aliases": [], "aliases": [], "redirects": []}
                if not val: val = {}

                # Get DocumentRoot
                if not "null_path" in val:
                    directory = dval["root"] + subdomain + "/"
                    if "path" in val:
                        if val["path"].startswith("/"): # Absolute
                            directory = val["path"]
                        else: # Relative
                            directory = directory + val["path"]

                    site["directory"] = directory
                else:
                    site["directory"] = self.structure["config"]["null_path"]

                if "no_path" in val:
                    del site["directory"]

                # Determine top-level vs subdomain
                full_domain = subdomain + "." + domain
                if "is_root" in val:
                    # Handle actual root and it's subdomain
                    site["domain"] = domain
                    site["domain_aliases"].append(full_domain)
                else:
                    site["domain"] = full_domain

                site["domain_rpn"] = '.'.join(reversed(full_domain.split('.')))

                # Aliases
                if "alt_names" in val:
                    site["domain_aliases"] = site["domain_aliases"].extend(val["alt_names"])

                # Let's Encrypt
                site["letsencrypt_domain"] = "letsencrypt" in dval or "letsencrypt" in val

                # Remove subdomain
                site["remove_subdomain"] = "remove_subdomain" in val

                # Handle redirect parameter
                is_https_redirect = False
                if "http" in val and "redirect" in val["http"]:
                    if "https" in val["http"]:
                        is_https_redirect = True
                    else:
                        site["redirects"].append({"target": val["http"]["redirect"]})

                # Auth
                if "auth" in val:
                    site["restrict"] = val["auth"]

                # FCGI
                if "fcgi" in val:
                    fcgi_type, fcgi_port, fcgi_socket = val["fcgi"].split(" ")
                    site["fcgi_config"] = {"type": fcgi_type, "port": fcgi_port, "socket": fcgi_socket}

                # WSGI
                if "wsgi" in val:
                    site["wsgi_config"] = Generator.listize(val["wsgi"])

                # Proxy
                if "proxy" in val and "sites" in val["proxy"]:
                    site["proxy"] = val["proxy"]

                # Extra
                if "extra_nginx" in val:
                    site["extra_nginx"] = val["extra_nginx"]

                # IPv6
                site["ipv6"] = "ipv6" in self.structure["config"] and not ("ipv6" in dval and "disabled" in dval["ipv6"]) and not ("ipv6" in val and "disabled" in val["ipv6"])

                # Handle HTTP site
                if not "http" in val or not "none" in val["http"]:
                    site["http"] = True

                    # Handle redirect only here
                    if is_https_redirect:
                        redir_site = copy.deepcopy(site)
                        redir_site["https_redirect"] = True
                        redir_site["redirects"].append({"target": "https://" + site["domain"] + "/"});
                        redir_site["directory"] = self.structure["config"]["null_path"]
                        output[domain].append(redir_site)

                # Handle HTTPS site (LE only for now)
                if "https" in val:
                    site["https"] = True
                    if is_https_redirect:
                        site["http"] = False

                output[domain].append(site)

            if "redir_domains" in dval and "domains" in dval["redir_domains"]:
                for rd in dval["redir_domains"]["domains"]:
                    site = {"domain": rd, "redirects": [{"target": dval["redir_domains"]["target"]}]}
                    output[domain].append(site)

        return output
