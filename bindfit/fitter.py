from __future__ import division
from __future__ import print_function

from math import sqrt
from copy import deepcopy
import time
from itertools import product

import numpy as np
import numpy.matlib as ml

import scipy
import scipy.optimize
from scipy import stats

from . import functions
from . import helpers 

import logging
logger = logging.getLogger('supramolecular')

class Fitter():
    def __init__(self, xdata, ydata, function, normalise=True):
        self.xdata = xdata # Original input data, no processing applied
        self.ydata = ydata # Original input data, no processing applied
        self.function = function

        # Fitter options
        self.normalise = normalise

        # Populated on Fitter.run
        self.params = None
        self.time = None
        self.fit = None
        self.residuals = None
        self.coeffs = None
        self.molefrac = None

    def _preprocess(self, ydata):
        # Preprocess data based on Fitter options
        # Returns modified processed copy of input data
        d = ydata

        if self.normalise:
            d = helpers.normalise(d)

        return d

    def _postprocess(self, ydata, yfit):
        # Postprocess fitted data based on Fitter options 
        f = yfit 

        if self.normalise:
            f = helpers.denormalise(ydata, yfit)

        return f 

    def run_scipy(self, params_init):
        """
        Arguments:
            params: dict  Initial parameter guesses for fitter    
        """
        logger.debug("Fitter.fit: called. Input params:")
        logger.debug(params_init)
        
        p = []
        for key, value in sorted(params_init.items()):
            p.append(value)
        
        # Run optimizer 
        x = self.xdata
        y = self._preprocess(self.ydata)

        tic = time.clock()
        result = scipy.optimize.minimize(self.function.objective,
                                         p,
                                         args=(x, y, True),
                                         method='Nelder-Mead',
                                         tol=1e-18,
                                        )
        toc = time.clock()

        logger.debug("Fitter.run: FIT FINISHED")
        logger.debug("Fitter.run: Fitter.function")
        logger.debug(self.function)
        logger.debug("Fitter.run: result.x")
        logger.debug(result.x)

        # Calculate fitted data with optimised parameters
        fit_norm, residuals, coeffs, molefrac = self.function.objective(
                                                    result.x, 
                                                    x, 
                                                    y, 
                                                    detailed=True,
                                                    force_molefrac=True)

        # Save time taken to fit
        self.time = toc - tic 

        # Save raw optimised params arra
        self._params_raw = result.x

        # Postprocess (denormalise) and save fitted data
        fit = self._postprocess(self.ydata, fit_norm)
        self.fit = fit

        self.residuals = residuals

        self.coeffs = coeffs

        # Calculate host molefraction from complexes and add as first row
        molefrac_host = np.ones(molefrac.shape[1])
        molefrac_host -= molefrac.sum(axis=0)
        self.molefrac = np.vstack((molefrac_host, molefrac))

        # Calculate fit uncertainty statistics
        ci = self.statistics()

        # Save final optimised parameters and errors as dictionary
        self.params = { name: {"value": param, "stderr": stderr, "init": params_init[name]} 
                        for (name, param, stderr) 
                        in zip(sorted(params_init), result.x, ci) }

        logger.debug("Fitter.run: PARAMS DICT")
        logger.debug(self.params)

    def statistics(self):
        """
        Return fit statistics after parameter optimisation

        Returns:
            Asymptotic error for non-linear parameter estimate
            # Standard deviation of calculated y
            # Standard deviation of calculated coefficients
        """
        # Calculate deLevie uncertainty
        d = np.float64(1e-6) # delta
        params = self._params_raw
        ##### TODO: DEBUG TEMP
        #params = np.array([115221.3827278451, 12990.4400058688])

        matlab_fit = np.array([
            0.260980004891973, 
            0.261356346284718,
            0.261728036526842,
            0.262095159604778,
            0.262457802288570,
            0.262993550336373,
            0.263519685132872,
            0.264206705618678,
            0.264877719496410,
            0.265533307260044,
            0.266174022576733,
            0.266800393649557,
            0.267412924517197,
            0.268012096291599,
            0.268598368335050,
            0.269172179378370,
            0.269733948582118,
            0.270284076542882,
            0.270822946246791,
            0.271350923972484,
            0.271868360145761,
            0.272375590148171,
            0.272872935081741,
            0.273360702492039,
            0.274075036987498,
            0.274769425785596,
            0.275444755107045,
            0.276316978818846,
            0.277158634322402,
            0.278367483015657,
            0.279516551623408,
            0.280963607186894,
            0.282322275589818,
            0.283909010713929,
            0.285384779249066,
            0.287286865316257,
            0.289720077091490,
            0.291874030873545,
            0.293796290957534,
            0.296323934036766,
            0.301009759277683,
            0.309148360101187,
            0.319118851731557,
            0.329588014577170,
            0.337870384086082,
            0.344619659554336,
            0.352712072520314,
            0.365725911315436,
            0.372034938785321,
            0.378483305364665,
            0.384294588691350,
            0.388820345850703,
            0.392115233903391,
            0.396591589497526,
            0.400588595691663,
            0.403636777149600,
            0.405841052479933,
            0.385300005835962,
            0.385749047775225,
            0.386192695884397,
            0.386631045382319,
            0.387064194955958,
            0.387704379665094,
            0.388333396688657,
            0.389155239444060,
            0.389958462749610,
            0.390743728326411,
            0.391511667706103,
            0.392262883751172,
            0.392997952105495,
            0.393717422576265,
            0.394421820448802,
            0.395111647736096,
            0.395787384365163,
            0.396449489302439,
            0.397098401620604,
            0.397734541509243,
            0.398358311231814,
            0.398970096031403,
            0.399570264987690,
            0.400159171827556,
            0.401022153680025,
            0.401861642433532,
            0.402678659853476,
            0.403734714549783,
            0.404754648747120,
            0.406221082832681,
            0.407616665280647,
            0.409376464170259,
            0.411031094654075,
            0.412966294016293,
            0.414768857393628,
            0.417095926234781,
            0.420078880549252,
            0.422725042372877,
            0.425090845006701,
            0.428207655910544,
            0.434002633749143,
            0.444114956144941,
            0.456572374661279,
            0.469717189517752,
            0.480152473262456,
            0.488674888253518,
            0.498911360009452,
            0.515405734030328,
            0.523413591826441,
            0.531604598572515,
            0.538991076197802,
            0.544746311324475,
            0.548937661024678,
            0.554633616547882,
            0.559721137908782,
            0.563601852607864,
            0.566408620169864,
            0.355999993598842,
            0.355507455354480,
            0.355020817816291,
            0.354539977041722,
            0.354064825269465,
            0.353362534947617,
            0.352672463776041,
            0.351770802731527,
            0.350889516734297,
            0.350027883059705,
            0.349185211914731,
            0.348360844780986,
            0.347554152833686,
            0.346764535435363,
            0.345991418702664,
            0.345234254144243,
            0.344492517367494,
            0.343765706851660,
            0.343053342784787,
            0.342354965961834,
            0.341670136741296,
            0.340998434057623,
            0.340339454486792,
            0.339692811362409,
            0.338745170667074,
            0.337823268129905,
            0.336925986580994,
            0.335766102379368,
            0.334645802167111,
            0.333034913911009,
            0.331501692612079,
            0.329568107864947,
            0.327749849288523,
            0.325622999375433,
            0.323641656529665,
            0.321083417436472,
            0.317803542909203,
            0.314893443315425,
            0.312291250921564,
            0.308862433604867,
            0.302485713019646,
            0.291353674844550,
            0.277633436732839,
            0.263149970274011,
            0.251648531691757,
            0.242253620359524,
            0.230967465158361,
            0.212778626558398,
            0.203947040217257,
            0.194912873481010,
            0.186765607883589,
            0.180417341479584,
            0.175793978332334,
            0.169510767140315,
            0.163898577694404,
            0.159617567596186,
            0.156521239935652,
            0.272779994840286,
            0.272382948648283,
            0.271990598013252,
            0.271602861103334,
            0.271219652950695,
            0.270653151122098,
            0.270096380689313,
            0.269368705221463,
            0.268657266495294,
            0.267961494034271,
            0.267280843194820,
            0.266614793872061,
            0.265962849264612,
            0.265324534697547,
            0.264699396502234,
            0.264087000951525,
            0.263486933248552,
            0.262898796567245,
            0.262322211142583,
            0.261756813408528,
            0.261202255181560,
            0.260658202887735,
            0.260124336831187,
            0.259600350502062,
            0.258832255692814,
            0.258084789069860,
            0.257357064045930,
            0.256416037539960,
            0.255506782162788,
            0.254198767355024,
            0.252953174640130,
            0.251381440068654,
            0.249902557513614,
            0.248171599123022,
            0.246558028755778,
            0.244473197089226,
            0.241797944836711,
            0.239422184367834,
            0.237296167996554,
            0.234492538211339,
            0.229272095697232,
            0.220140766040664,
            0.208860517628652,
            0.196928762631071,
            0.187440240576179,
            0.179682644866061,
            0.170356744501105,
            0.155315076523804,
            0.148007377218997,
            0.140529745339582,
            0.133784475627655,
            0.128527628146258,
            0.124698632252871,
            0.119494358600864,
            0.114845325973059,
            0.111298692351821,
            0.108733352713190])

        matlab_fit_shift_0 = np.array([
            0.260980004891978, 
            0.261356346580314,
            0.261728037110623,
            0.262095160469532,
            0.262457803427280,
            0.262993551873266,
            0.263519687053193,
            0.264206708028299,
            0.264877722371476,
            0.265533310577958,
            0.266174026316089,
            0.266800397790072,
            0.267412929039652,
            0.268012101177777,
            0.268598373567683,
            0.269172184941085,
            0.269733954459387,
            0.270284082719974,
            0.270822952709730,
            0.271350930708004,
            0.271868367141270,
            0.272375597391711,
            0.272872942561952,
            0.273360710198130,
            0.274075045013337,
            0.274769434109782,
            0.275444763709727,
            0.276316987764421,
            0.277158643581164,
            0.278367492694432,
            0.279516561669586,
            0.280963617652901,
            0.282322286407962,
            0.283909021893805,
            0.285384790719541,
            0.287286877099476,
            0.289720089179861,
            0.291874043150006,
            0.293796303342213,
            0.296323946485835,
            0.301009771642543,
            0.309148371834221,
            0.319118862152503,
            0.329588023310577,
            0.337870391420149,
            0.344619665767784,
            0.352712077458121,
            0.365725914439214,
            0.372034941159482,
            0.378483307070897,
            0.384294589885405,
            0.388820346706979,
            0.392115234548177,
            0.396591589902221,
            0.400588595928547,
            0.403636777288338,
            0.405841052563887,
            0.385300005835968,
            0.385749048127907,
            0.386192696581010,
            0.386631046414345,
            0.387064196315105,
            0.387704381499861,
            0.388333398981606,
            0.389155242321987,
            0.389958466184308,
            0.390743732291150,
            0.391511672175554,
            0.392262888701326,
            0.392997957513593,
            0.393717428420727,
            0.394421826709163,
            0.395111654392945,
            0.395787391400081,
            0.396449496697948,
            0.397098409360114,
            0.397734549577001,
            0.398358319612859,
            0.398970104711520,
            0.399570273953374,
            0.400159181065968,
            0.401022163304828,
            0.401861652419241,
            0.402678670176431,
            0.403734725288488,
            0.404754659866115,
            0.406221094462643,
            0.407616677358632,
            0.409376476761675,
            0.411031107677663,
            0.412966307485739,
            0.414768871223168,
            0.417095940454686,
            0.420078895154947,
            0.422725057221622,
            0.425090860000531,
            0.428207671001001,
            0.434002648771431,
            0.444114970453289,
            0.456572387423353,
            0.469717200255326,
            0.480152482304418,
            0.488674895929420,
            0.498911366122847,
            0.515405737909628,
            0.523413594778645,
            0.531604600696754,
            0.538991077685894,
            0.544746312392400,
            0.548937661829251,
            0.554633617053201,
            0.559721138204731,
            0.563601852781266,
            0.566408620274825,
            0.355999993598836,
            0.355507454967637,
            0.355020817052195,
            0.354539975909708,
            0.354064823778618,
            0.353362532935029,
            0.352672461260820,
            0.351770799574548,
            0.350889512966475,
            0.350027878710334,
            0.349185207011573,
            0.348360839350357,
            0.347554146900533,
            0.346764529023340,
            0.345991411834203,
            0.345234246840626,
            0.344492509648909,
            0.343765698737270,
            0.343053334292781,
            0.342354957109484,
            0.341670127545005,
            0.340998424532976,
            0.340339444648600,
            0.339692801224750,
            0.338745160105107,
            0.337823257171581,
            0.336925975252260,
            0.335766090593951,
            0.334645789963905,
            0.333034901146360,
            0.331501679355045,
            0.329568094043497,
            0.327749834991837,
            0.325622984588275,
            0.323641641346194,
            0.321083401823103,
            0.317803526870503,
            0.314893427008268,
            0.312291234453670,
            0.308862417029005,
            0.302485696515323,
            0.291353659119326,
            0.277633422701738,
            0.263149958464608,
            0.251648521744811,
            0.242253611913858,
            0.230967458430602,
            0.212778622288109,
            0.203947036967137,
            0.194912871142159,
            0.186765606245010,
            0.180417340303587,
            0.175793977446301,
            0.169510766583802,
            0.163898577368456,
            0.159617567405200,
            0.156521239820044,
            0.272779994840281,
            0.272382948336446,
            0.271990597397274,
            0.271602860190706,
            0.271219651748707,
            0.270653149499320,
            0.270096378661083,
            0.269368702675444,
            0.268657263456306,
            0.267961490525838,
            0.267280839239239,
            0.266614789490469,
            0.265962844477051,
            0.265324529523026,
            0.264699390958781,
            0.264086995056246,
            0.263486927017679,
            0.262898790016186,
            0.262322204285968,
            0.261756806260251,
            0.261202247754819,
            0.260658195195070,
            0.260124328884521,
            0.259600342312727,
            0.258832247159523,
            0.258084780215125,
            0.257357054890656,
            0.256416028013946,
            0.255506772297395,
            0.254198757033187,
            0.252953163917586,
            0.251381428886217,
            0.249902545943366,
            0.248171587151804,
            0.246558016459842,
            0.244473184439989,
            0.241797931836095,
            0.239422171143501,
            0.237296154636384,
            0.234492524756365,
            0.229272082287251,
            0.220140753243063,
            0.208860506189157,
            0.196928752986840,
            0.187440232443498,
            0.179682637954960,
            0.170356738990716,
            0.155315073021760,
            0.148007374552150,
            0.140529743419496,
            0.133784474281895,
            0.128527627180120,
            0.124698631524798,
            0.119494358143439,
            0.114845325705085,
            0.111298692194777,
            0.108733352618117])

        matlab_fit_shift_1 = np.array([
            0.260980004891973, 
            0.261356346285912,
            0.261728036531563,
            0.262095159615274,
            0.262457802307010,
            0.262993550370621,
            0.263519685187378,
            0.264206705706696,
            0.264877719624877,
            0.265533307435388,
            0.266174022804904,
            0.266800393936060,
            0.267412924867118,
            0.268012096709632,
            0.268598368825524,
            0.269172179945269,
            0.269733949229106,
            0.270284077273321,
            0.270822947063764,
            0.271350924878810,
            0.271868361144015,
            0.272375591240696,
            0.272872936270666,
            0.273360703779292,
            0.274075038425453,
            0.274769427377589,
            0.275444756855887,
            0.276316980780381,
            0.277158636499791,
            0.278367485520880,
            0.279516554459171,
            0.280963610464179,
            0.282322279306206,
            0.283909014971655,
            0.285384784036250,
            0.287286870820084,
            0.289720083562872,
            0.291874038243159,
            0.293796299157071,
            0.296323943361168,
            0.301009770758880,
            0.309148375400733,
            0.319118871484655,
            0.329588038303768,
            0.337870410195651,
            0.344619686997320,
            0.352712100749537,
            0.365725938759443,
            0.372034964875368,
            0.378483329383559,
            0.384294610234014,
            0.388820365057571,
            0.392115251182800,
            0.396591603849397,
            0.400588607126716,
            0.403636786167231,
            0.405841059644998,
            0.385300005835962,
            0.385749047776729,
            0.386192695890341,
            0.386631045395536,
            0.387064194979177,
            0.387704379708222,
            0.388333396757296,
            0.389155239554907,
            0.389958462911403,
            0.390743728547251,
            0.391511667993493,
            0.392262884112051,
            0.392997952546277,
            0.393717423102872,
            0.394421821066695,
            0.395111648450305,
            0.395787385180313,
            0.396449490222779,
            0.397098402650029,
            0.397734542651317,
            0.398358312489792,
            0.398970097408249,
            0.399570266486101,
            0.400159173449975,
            0.401022155492522,
            0.401861644440342,
            0.402678662058171,
            0.403734717022857,
            0.404754651492607,
            0.406221085991992,
            0.407616668857298,
            0.409376468304529,
            0.411031099343077,
            0.412966299389405,
            0.414768863436064,
            0.417095933183520,
            0.420078888722210,
            0.422725051682936,
            0.425090855367867,
            0.428207667697084,
            0.434002648270866,
            0.444114975515671,
            0.456572399698249,
            0.469717219621095,
            0.480152506411688,
            0.488674923112701,
            0.498911395885957,
            0.515405768933513,
            0.523413625017416,
            0.531604629136971,
            0.538991103617377,
            0.544746335775018,
            0.548937683024011,
            0.554633634822649,
            0.559721152471228,
            0.563601864092760,
            0.566408629295890,
            0.355999993598842,
            0.355507455352822,
            0.355020817809739,
            0.354539977027156,
            0.354064825243875,
            0.353362534900086,
            0.352672463700393,
            0.351770802609361,
            0.350889516555980,
            0.350027882816309,
            0.349185211597987,
            0.348360844383246,
            0.347554152347880,
            0.346764534854962,
            0.345991418021649,
            0.345234253357070,
            0.344492516469062,
            0.343765705837287,
            0.343053341650179,
            0.342354964703062,
            0.341670135354771,
            0.340998432540075,
            0.340339452835249,
            0.339692809574178,
            0.338745168669325,
            0.337823265917968,
            0.336925984150929,
            0.335766099653466,
            0.334645799140921,
            0.333034910428643,
            0.331501688669652,
            0.329568103307803,
            0.327749844119831,
            0.325622993452541,
            0.323641649868853,
            0.321083409776442,
            0.317803533899388,
            0.314893433051824,
            0.312291239498948,
            0.308862420610481,
            0.302485697008945,
            0.291353653485815,
            0.277633409123738,
            0.263149937075225,
            0.251648495131768,
            0.242253581912043,
            0.230967425587089,
            0.212778588058372,
            0.203947003604973,
            0.194912839765200,
            0.186765577636336,
            0.180417314507175,
            0.175793954063726,
            0.169510746980222,
            0.163898561629449,
            0.159617554926217,
            0.156521229867902,
            0.272779994840286,
            0.272382948646916,
            0.271990598007849,
            0.271602861091320,
            0.271219652929588,
            0.270653151082894,
            0.270096380626917,
            0.269368705120696,
            0.268657266348210,
            0.267961493833503,
            0.267280842933546,
            0.266614793543967,
            0.265962848863864,
            0.265324534218757,
            0.264699395940434,
            0.264087000302136,
            0.263486932507364,
            0.262898795730390,
            0.262322210206515,
            0.261756812370001,
            0.261202254037609,
            0.260658201635657,
            0.260124335468526,
            0.259600349026590,
            0.258832254044418,
            0.258084787244675,
            0.257357062040695,
            0.256416035290516,
            0.255506779665445,
            0.254198764481057,
            0.252953171386293,
            0.251381436307194,
            0.249902553247085,
            0.248171594233528,
            0.246558023256682,
            0.244473190764542,
            0.241797937396566,
            0.239422175891344,
            0.237296158561875,
            0.234492527476972,
            0.229272082467885,
            0.220140748385169,
            0.208860494796345,
            0.196928735165166,
            0.187440210321248,
            0.179682613042909,
            0.170356711740966,
            0.155315044641510,
            0.148007346896392,
            0.140529717412810,
            0.133784450571631,
            0.128527605801574,
            0.124698612147188,
            0.119494341897975,
            0.114845312662395,
            0.111298681853711,
            0.108733344371026])
        ##### TODO: END DEBUG TEMP
         
        ##### TODO: DEBUG TEMP!
        np.set_printoptions(precision=15)
        ##### TODO: END DEBUG TEMP!

        # 0. Calculate partial differentials for each parameter
        diffs = []
        for i, pi in enumerate(params):
            # Shift the ith parameter's value by delta
            pi_shift = pi*(1 + d)
            logger.debug("Fitter.statistics: pi_shift, iteration "+str(i))
            logger.debug(pi_shift.dtype)
            logger.debug(pi_shift)
            logger.debug("Fitter.statistics: (1 + d)")
            logger.debug((1 + d))
            params_shift = np.copy(params)
            params_shift[i] = pi_shift

            logger.debug("Fitter.statistics: params_shift, iteration "+str(i))
            logger.debug(params_shift.dtype)
            logger.debug(params_shift)
            logger.debug("... vs. original params")
            logger.debug(params.dtype)
            logger.debug(params)

            # Calculate fit with modified parameter set
            x   = self.xdata
            logger.debug("Fitter.statistics: self.xdata dtype")
            logger.debug(self.xdata.dtype)
            y   = self._preprocess(self.ydata)
            fit_shift_norm, _, _, _ = self.function.objective(params_shift, 
                                                        x, 
                                                        y, 
                                                        detailed=True,
                                                        force_molefrac=True)
            fit_shift = self._postprocess(self.ydata, fit_shift_norm)
            
            ##### TODO: DEBUG! 
            if i == 0:
                fit_shift = matlab_fit_shift_0
            elif i == 1:
                fit_shift = matlab_fit_shift_1
            ##### TODO: END DEBUG! 

            logger.debug("Fitter.statistics: fit_shift")
            logger.debug(fit_shift.dtype)
            logger.debug(fit_shift)
            logger.debug("Fitter.statistics: fit")
            logger.debug(self.fit.dtype)
            logger.debug(self.fit)

            # Calculate partial differential
            # Flatten numerator into 1D array (TODO: is this correct?)
            #num   = (fit_shift - self.fit).flatten()
            ##### TODO: DEBUG
            num   = (fit_shift - matlab_fit).flatten()
            ##### TODO: END DEBUG
            denom = pi_shift - pi
            diffs.append(np.divide(num, denom))

            logger.debug("Fitter.statistics: num (fit_shift - fit)")
            logger.debug(num.dtype)
            logger.debug(num)
            logger.debug("Fitter.statistics: denom (pi_shift - pi)")
            logger.debug(denom.dtype)
            logger.debug(denom)
            logger.debug("Fitter.statistics: num/denom")
            logger.debug(num/denom)

        diffs = np.array(diffs)

        logger.debug("Fitter.statistics: diffs array")
        logger.debug(diffs.dtype)
        logger.debug(diffs[0].dtype)
        logger.debug(diffs)

        # 1. Calculate PxP matrix M and invert
        P = len(params)
        M = np.zeros((P, P))
        for i, j in product(range(P), range(P)):
            M[i, j] = np.sum(diffs[i]*diffs[j])

        # TODO TEMP set M manually to match UV 1:2 result in Matlab
        # M = np.array([[1.1951e-12, 8.7884e-12], [8.7884e-12, 264.9524e-12]])
        # M = np.array([[np.sum(diffs[0]**2), np.sum(diffs[0]*diffs[1])], [np.sum(diffs[0]*diffs[1]), np.sum(diffs[1]**2)]])

        M_inv = np.linalg.inv(M)
        m_diag = np.diagonal(M_inv)
        logger.debug("Fitter.statistics: M before inversion")
        logger.debug(M)
        logger.debug("Fitter.statistics: M after inversion")
        logger.debug(M_inv)
        logger.debug("Fitter.statistics: m_diag")
        logger.debug(m_diag)

        # 2. Calculate standard deviations sigma of P parameters pi
        # Sum of squares of residuals
        ssr = np.sum(np.square(self.residuals))
        logger.debug("Fitter.statistics: ssr")
        logger.debug(ssr)
        # Degrees of freedom:
        # N datapoints - N fitted params - N calculated coefficients
        d_free = self.ydata.size - len(params) - self.coeffs.size
        logger.debug("Fitter.statistics: d_free")
        logger.debug(d_free)

        # TODO why d_free - 1?
        sigma = np.sqrt((m_diag*ssr)/(d_free - 1))

        # 3. Calculate confidence intervals
        # Calculate t-value at 95%
        # Studnt, n=d_free, p<0.05, 2-tail
        t = stats.t.ppf(1 - 0.025, d_free)

        logger.debug("Fitter.statistics: t_value")
        logger.debug(t)
        logger.debug("Fitter.statistics: sigma")
        logger.debug(sigma)

        ci = np.array([params - t*sigma, params + t*sigma])
        ci_percent = (t*sigma)/params * 100

        logger.debug("Fitter.statistics: ci, ci_percent")
        logger.debug("+/- "+str(t*sigma))
        logger.debug("% "+str(ci_percent))

        return ci_percent
