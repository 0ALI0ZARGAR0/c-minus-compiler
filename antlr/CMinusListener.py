# Generated from CMinus.g4 by ANTLR 4.9.2
from antlr4 import *
if __name__ is not None and "." in __name__:
    from .CMinusParser import CMinusParser
else:
    from CMinusParser import CMinusParser

# This class defines a complete listener for a parse tree produced by CMinusParser.
class CMinusListener(ParseTreeListener):

    # Enter a parse tree produced by CMinusParser#program.
    def enterProgram(self, ctx:CMinusParser.ProgramContext):
        pass

    # Exit a parse tree produced by CMinusParser#program.
    def exitProgram(self, ctx:CMinusParser.ProgramContext):
        pass


    # Enter a parse tree produced by CMinusParser#declaration_list.
    def enterDeclaration_list(self, ctx:CMinusParser.Declaration_listContext):
        pass

    # Exit a parse tree produced by CMinusParser#declaration_list.
    def exitDeclaration_list(self, ctx:CMinusParser.Declaration_listContext):
        pass


    # Enter a parse tree produced by CMinusParser#declaration.
    def enterDeclaration(self, ctx:CMinusParser.DeclarationContext):
        pass

    # Exit a parse tree produced by CMinusParser#declaration.
    def exitDeclaration(self, ctx:CMinusParser.DeclarationContext):
        pass


    # Enter a parse tree produced by CMinusParser#declaration_initial.
    def enterDeclaration_initial(self, ctx:CMinusParser.Declaration_initialContext):
        pass

    # Exit a parse tree produced by CMinusParser#declaration_initial.
    def exitDeclaration_initial(self, ctx:CMinusParser.Declaration_initialContext):
        pass


    # Enter a parse tree produced by CMinusParser#declaration_prime.
    def enterDeclaration_prime(self, ctx:CMinusParser.Declaration_primeContext):
        pass

    # Exit a parse tree produced by CMinusParser#declaration_prime.
    def exitDeclaration_prime(self, ctx:CMinusParser.Declaration_primeContext):
        pass


    # Enter a parse tree produced by CMinusParser#var_declaration_prime.
    def enterVar_declaration_prime(self, ctx:CMinusParser.Var_declaration_primeContext):
        pass

    # Exit a parse tree produced by CMinusParser#var_declaration_prime.
    def exitVar_declaration_prime(self, ctx:CMinusParser.Var_declaration_primeContext):
        pass


    # Enter a parse tree produced by CMinusParser#fun_declaration_prime.
    def enterFun_declaration_prime(self, ctx:CMinusParser.Fun_declaration_primeContext):
        pass

    # Exit a parse tree produced by CMinusParser#fun_declaration_prime.
    def exitFun_declaration_prime(self, ctx:CMinusParser.Fun_declaration_primeContext):
        pass


    # Enter a parse tree produced by CMinusParser#type_specifier.
    def enterType_specifier(self, ctx:CMinusParser.Type_specifierContext):
        pass

    # Exit a parse tree produced by CMinusParser#type_specifier.
    def exitType_specifier(self, ctx:CMinusParser.Type_specifierContext):
        pass


    # Enter a parse tree produced by CMinusParser#params.
    def enterParams(self, ctx:CMinusParser.ParamsContext):
        pass

    # Exit a parse tree produced by CMinusParser#params.
    def exitParams(self, ctx:CMinusParser.ParamsContext):
        pass


    # Enter a parse tree produced by CMinusParser#param_list.
    def enterParam_list(self, ctx:CMinusParser.Param_listContext):
        pass

    # Exit a parse tree produced by CMinusParser#param_list.
    def exitParam_list(self, ctx:CMinusParser.Param_listContext):
        pass


    # Enter a parse tree produced by CMinusParser#param.
    def enterParam(self, ctx:CMinusParser.ParamContext):
        pass

    # Exit a parse tree produced by CMinusParser#param.
    def exitParam(self, ctx:CMinusParser.ParamContext):
        pass


    # Enter a parse tree produced by CMinusParser#param_prime.
    def enterParam_prime(self, ctx:CMinusParser.Param_primeContext):
        pass

    # Exit a parse tree produced by CMinusParser#param_prime.
    def exitParam_prime(self, ctx:CMinusParser.Param_primeContext):
        pass


    # Enter a parse tree produced by CMinusParser#compound_stmt.
    def enterCompound_stmt(self, ctx:CMinusParser.Compound_stmtContext):
        pass

    # Exit a parse tree produced by CMinusParser#compound_stmt.
    def exitCompound_stmt(self, ctx:CMinusParser.Compound_stmtContext):
        pass


    # Enter a parse tree produced by CMinusParser#statement_list.
    def enterStatement_list(self, ctx:CMinusParser.Statement_listContext):
        pass

    # Exit a parse tree produced by CMinusParser#statement_list.
    def exitStatement_list(self, ctx:CMinusParser.Statement_listContext):
        pass


    # Enter a parse tree produced by CMinusParser#statement.
    def enterStatement(self, ctx:CMinusParser.StatementContext):
        pass

    # Exit a parse tree produced by CMinusParser#statement.
    def exitStatement(self, ctx:CMinusParser.StatementContext):
        pass


    # Enter a parse tree produced by CMinusParser#expression_stmt.
    def enterExpression_stmt(self, ctx:CMinusParser.Expression_stmtContext):
        pass

    # Exit a parse tree produced by CMinusParser#expression_stmt.
    def exitExpression_stmt(self, ctx:CMinusParser.Expression_stmtContext):
        pass


    # Enter a parse tree produced by CMinusParser#selection_stmt.
    def enterSelection_stmt(self, ctx:CMinusParser.Selection_stmtContext):
        pass

    # Exit a parse tree produced by CMinusParser#selection_stmt.
    def exitSelection_stmt(self, ctx:CMinusParser.Selection_stmtContext):
        pass


    # Enter a parse tree produced by CMinusParser#else_stmt.
    def enterElse_stmt(self, ctx:CMinusParser.Else_stmtContext):
        pass

    # Exit a parse tree produced by CMinusParser#else_stmt.
    def exitElse_stmt(self, ctx:CMinusParser.Else_stmtContext):
        pass


    # Enter a parse tree produced by CMinusParser#iteration_stmt.
    def enterIteration_stmt(self, ctx:CMinusParser.Iteration_stmtContext):
        pass

    # Exit a parse tree produced by CMinusParser#iteration_stmt.
    def exitIteration_stmt(self, ctx:CMinusParser.Iteration_stmtContext):
        pass


    # Enter a parse tree produced by CMinusParser#return_stmt.
    def enterReturn_stmt(self, ctx:CMinusParser.Return_stmtContext):
        pass

    # Exit a parse tree produced by CMinusParser#return_stmt.
    def exitReturn_stmt(self, ctx:CMinusParser.Return_stmtContext):
        pass


    # Enter a parse tree produced by CMinusParser#return_stmt_prime.
    def enterReturn_stmt_prime(self, ctx:CMinusParser.Return_stmt_primeContext):
        pass

    # Exit a parse tree produced by CMinusParser#return_stmt_prime.
    def exitReturn_stmt_prime(self, ctx:CMinusParser.Return_stmt_primeContext):
        pass


    # Enter a parse tree produced by CMinusParser#expression.
    def enterExpression(self, ctx:CMinusParser.ExpressionContext):
        pass

    # Exit a parse tree produced by CMinusParser#expression.
    def exitExpression(self, ctx:CMinusParser.ExpressionContext):
        pass


    # Enter a parse tree produced by CMinusParser#b.
    def enterB(self, ctx:CMinusParser.BContext):
        pass

    # Exit a parse tree produced by CMinusParser#b.
    def exitB(self, ctx:CMinusParser.BContext):
        pass


    # Enter a parse tree produced by CMinusParser#h.
    def enterH(self, ctx:CMinusParser.HContext):
        pass

    # Exit a parse tree produced by CMinusParser#h.
    def exitH(self, ctx:CMinusParser.HContext):
        pass


    # Enter a parse tree produced by CMinusParser#simple_expression_zegond.
    def enterSimple_expression_zegond(self, ctx:CMinusParser.Simple_expression_zegondContext):
        pass

    # Exit a parse tree produced by CMinusParser#simple_expression_zegond.
    def exitSimple_expression_zegond(self, ctx:CMinusParser.Simple_expression_zegondContext):
        pass


    # Enter a parse tree produced by CMinusParser#simple_expression_prime.
    def enterSimple_expression_prime(self, ctx:CMinusParser.Simple_expression_primeContext):
        pass

    # Exit a parse tree produced by CMinusParser#simple_expression_prime.
    def exitSimple_expression_prime(self, ctx:CMinusParser.Simple_expression_primeContext):
        pass


    # Enter a parse tree produced by CMinusParser#c.
    def enterC(self, ctx:CMinusParser.CContext):
        pass

    # Exit a parse tree produced by CMinusParser#c.
    def exitC(self, ctx:CMinusParser.CContext):
        pass


    # Enter a parse tree produced by CMinusParser#relop.
    def enterRelop(self, ctx:CMinusParser.RelopContext):
        pass

    # Exit a parse tree produced by CMinusParser#relop.
    def exitRelop(self, ctx:CMinusParser.RelopContext):
        pass


    # Enter a parse tree produced by CMinusParser#additive_expression.
    def enterAdditive_expression(self, ctx:CMinusParser.Additive_expressionContext):
        pass

    # Exit a parse tree produced by CMinusParser#additive_expression.
    def exitAdditive_expression(self, ctx:CMinusParser.Additive_expressionContext):
        pass


    # Enter a parse tree produced by CMinusParser#additive_expression_prime.
    def enterAdditive_expression_prime(self, ctx:CMinusParser.Additive_expression_primeContext):
        pass

    # Exit a parse tree produced by CMinusParser#additive_expression_prime.
    def exitAdditive_expression_prime(self, ctx:CMinusParser.Additive_expression_primeContext):
        pass


    # Enter a parse tree produced by CMinusParser#additive_expression_zegond.
    def enterAdditive_expression_zegond(self, ctx:CMinusParser.Additive_expression_zegondContext):
        pass

    # Exit a parse tree produced by CMinusParser#additive_expression_zegond.
    def exitAdditive_expression_zegond(self, ctx:CMinusParser.Additive_expression_zegondContext):
        pass


    # Enter a parse tree produced by CMinusParser#d.
    def enterD(self, ctx:CMinusParser.DContext):
        pass

    # Exit a parse tree produced by CMinusParser#d.
    def exitD(self, ctx:CMinusParser.DContext):
        pass


    # Enter a parse tree produced by CMinusParser#addop.
    def enterAddop(self, ctx:CMinusParser.AddopContext):
        pass

    # Exit a parse tree produced by CMinusParser#addop.
    def exitAddop(self, ctx:CMinusParser.AddopContext):
        pass


    # Enter a parse tree produced by CMinusParser#term.
    def enterTerm(self, ctx:CMinusParser.TermContext):
        pass

    # Exit a parse tree produced by CMinusParser#term.
    def exitTerm(self, ctx:CMinusParser.TermContext):
        pass


    # Enter a parse tree produced by CMinusParser#term_prime.
    def enterTerm_prime(self, ctx:CMinusParser.Term_primeContext):
        pass

    # Exit a parse tree produced by CMinusParser#term_prime.
    def exitTerm_prime(self, ctx:CMinusParser.Term_primeContext):
        pass


    # Enter a parse tree produced by CMinusParser#term_zegond.
    def enterTerm_zegond(self, ctx:CMinusParser.Term_zegondContext):
        pass

    # Exit a parse tree produced by CMinusParser#term_zegond.
    def exitTerm_zegond(self, ctx:CMinusParser.Term_zegondContext):
        pass


    # Enter a parse tree produced by CMinusParser#g.
    def enterG(self, ctx:CMinusParser.GContext):
        pass

    # Exit a parse tree produced by CMinusParser#g.
    def exitG(self, ctx:CMinusParser.GContext):
        pass


    # Enter a parse tree produced by CMinusParser#factor.
    def enterFactor(self, ctx:CMinusParser.FactorContext):
        pass

    # Exit a parse tree produced by CMinusParser#factor.
    def exitFactor(self, ctx:CMinusParser.FactorContext):
        pass


    # Enter a parse tree produced by CMinusParser#var_call_prime.
    def enterVar_call_prime(self, ctx:CMinusParser.Var_call_primeContext):
        pass

    # Exit a parse tree produced by CMinusParser#var_call_prime.
    def exitVar_call_prime(self, ctx:CMinusParser.Var_call_primeContext):
        pass


    # Enter a parse tree produced by CMinusParser#var_prime.
    def enterVar_prime(self, ctx:CMinusParser.Var_primeContext):
        pass

    # Exit a parse tree produced by CMinusParser#var_prime.
    def exitVar_prime(self, ctx:CMinusParser.Var_primeContext):
        pass


    # Enter a parse tree produced by CMinusParser#factor_prime.
    def enterFactor_prime(self, ctx:CMinusParser.Factor_primeContext):
        pass

    # Exit a parse tree produced by CMinusParser#factor_prime.
    def exitFactor_prime(self, ctx:CMinusParser.Factor_primeContext):
        pass


    # Enter a parse tree produced by CMinusParser#factor_zegond.
    def enterFactor_zegond(self, ctx:CMinusParser.Factor_zegondContext):
        pass

    # Exit a parse tree produced by CMinusParser#factor_zegond.
    def exitFactor_zegond(self, ctx:CMinusParser.Factor_zegondContext):
        pass


    # Enter a parse tree produced by CMinusParser#args.
    def enterArgs(self, ctx:CMinusParser.ArgsContext):
        pass

    # Exit a parse tree produced by CMinusParser#args.
    def exitArgs(self, ctx:CMinusParser.ArgsContext):
        pass


    # Enter a parse tree produced by CMinusParser#arg_list.
    def enterArg_list(self, ctx:CMinusParser.Arg_listContext):
        pass

    # Exit a parse tree produced by CMinusParser#arg_list.
    def exitArg_list(self, ctx:CMinusParser.Arg_listContext):
        pass


    # Enter a parse tree produced by CMinusParser#arg_list_prime.
    def enterArg_list_prime(self, ctx:CMinusParser.Arg_list_primeContext):
        pass

    # Exit a parse tree produced by CMinusParser#arg_list_prime.
    def exitArg_list_prime(self, ctx:CMinusParser.Arg_list_primeContext):
        pass



del CMinusParser