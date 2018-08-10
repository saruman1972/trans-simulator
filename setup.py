from distutils.core import setup
import py2exe
import glob

setup(
    windows=[
        {"script":"MainFrame.py", "icon_resources":[(1,"icons/Simulator.ico")]}
    ],
    options={
        'py2exe':
        {
            'includes': ['lxml.etree', 'lxml._elementpath', 'gzip'],
        }
    },
    data_files=[
        ("icons", glob.glob("icons/*.ico")),
        (".", glob.glob("*.xml")),
        (".", glob.glob("*.txt")),
        ("project", glob.glob("project/*.prj")),
        ("project/aicBank", glob.glob("project/aicBank/*.xml")),
        ("project/aicBank/dictionary", glob.glob("project/aicBank/dictionary/*.xml")),
        ("project/aicBank/management_cases", glob.glob("project/aicBank/management_cases/*.xml")),
        ("project/aicBank/trans_cases", glob.glob("project/aicBank/trans_cases/*.xml")),
        ("project/bos1.0", glob.glob("project/bos1.0/*.xml")),
        ("project/bos1.0/dictionary", glob.glob("project/bos1.0/dictionary/*.xml")),
        ("project/bos1.0/management_cases", glob.glob("project/bos1.0/management_cases/*.xml")),
        ("project/bos1.0/trans_cases", glob.glob("project/bos1.0/trans_cases/*.xml")),
        ("project/bos2.1", glob.glob("project/bos2.1/*.xml")),
        ("project/bos2.1/dictionary", glob.glob("project/bos2.1/dictionary/*.xml")),
        ("project/bos2.1/management_cases", glob.glob("project/bos2.1/management_cases/*.xml")),
        ("project/bos2.1/trans_cases", glob.glob("project/bos2.1/trans_cases/*.xml")),
        ("project/jcb", glob.glob("project/jcb/*.xml")),
        ("project/jcb/dictionary", glob.glob("project/jcb/dictionary/*.xml")),
        ("project/jcb/management_cases", glob.glob("project/jcb/management_cases/*.xml")),
        ("project/jcb/trans_cases", glob.glob("project/jcb/trans_cases/*.xml")),
        ("project/mastercard", glob.glob("project/mastercard/*.xml")),
        ("project/mastercard/dictionary", glob.glob("project/mastercard/dictionary/*.xml")),
        ("project/mastercard/management_cases", glob.glob("project/mastercard/management_cases/*.xml")),
        ("project/mastercard/trans_cases", glob.glob("project/mastercard/trans_cases/*.xml")),
        ("project/topcard", glob.glob("project/topcard/*.xml")),
        ("project/topcard/dictionary", glob.glob("project/topcard/dictionary/*.xml")),
        ("project/topcard/management_cases", glob.glob("project/topcard/management_cases/*.xml")),
        ("project/topcard/trans_cases", glob.glob("project/topcard/trans_cases/*.xml")),
        ("project/visa", glob.glob("project/visa/*.xml")),
        ("project/visa/dictionary", glob.glob("project/visa/dictionary/*.xml")),
        ("project/visa/management_cases", glob.glob("project/visa/management_cases/*.xml")),
        ("project/visa/trans_cases", glob.glob("project/visa/trans_cases/*.xml"))
    ]
)
