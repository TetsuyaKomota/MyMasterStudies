import GenerateModelwithMakerMotions as generator
import EncodeModelwithSOINN as encoder
import ParsingModelwithNPYLM as parser
import PrunningModel as prunner
import MatchingModelwithNN as matcher

if __name__ == "__main__":
    print("+--------")
    generator.generate("tmp/log/", 1000)
    print("++-------")
    generator.generate("tmp/log_test/", 100)
    print("+++------")
    encoder.predict("tmp/log/")
    print("++++-----")
    encoder.predict("tmp/log_test/")
    print("+++++----")
    parser.parsing("encoded.dill")
    print("++++++---")
    parser.parsing("encoded_test.dill")
    print("+++++++--")
    prunner.prunning()
    print("++++++++-")
    matcher.matching() 
    print("+++++++++")
