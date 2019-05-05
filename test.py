import connector as c
import argparse

main_parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
main_parser.add_argument("--dbfile", "-d",
                             help='full name of the *.db file to use as data source',
                             default="LSST_archi_tool.db")
args = main_parser.parse_args()

print(c.link_short(args, '635bb685-bacb-43e3-b898-b7be4f94ed56', '711450b4-457b-4229-8e36-a501d464820d'))
print(c.link_short_all(args, '635bb685-bacb-43e3-b898-b7be4f94ed56', '711450b4-457b-4229-8e36-a501d464820d'))
a = c.link_all(args, '635bb685-bacb-43e3-b898-b7be4f94ed56', '711450b4-457b-4229-8e36-a501d464820d')


for entry in a:
    print(entry)
