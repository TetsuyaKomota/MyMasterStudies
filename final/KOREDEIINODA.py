import GenerateModelwithMakerMotions as generator
import EncodeModelwithSOINN as encoder
import ParsingModelwithNPYLM as parser
import PrunningModel as prunner
import MatchingModelwithNN as matcher

if __name__ == "__main__":
    generator.generate("tmp/log/", numTrain)
    generator.generate("tmp/log_test/", numTest)
    encoder.predict("test/", "tmp/log/", 5, 5000000, 100)
    encoder.predict("test/", "tmp/log_test/", 5, 5000000, 100)
    parser.parsing("test/", "encoded.dill", 2, 200)
    parser.parsing("test/", "encoded_test.dill", 2, 200)
    prunner.prunning("test/")
    matcher.matching("test/") 
