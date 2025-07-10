from django.urls import path
from .views import *

urlpatterns = [
    #--------------------Source api urls -----------------------
    path('createSource/',createSource, name='create_source'),
    path('getSource/<int:SourceId>/', getSource, name='get_sources'),
    path('updateSource/<int:SourceId>/',updateSource , name='update_source'),
    path('deleteSource/<int:SourceId>/', deleteSource, name='delete_source'),
    path('bulkCreateSource/',bulkCreateSource,name='bulk_createSource'),
    path('bulkUpdateSource/',bulkUpdateSource,name='bulk_updateSource'),
    path('viewAllSources/',viewAllSources,name='view_allSources'),
    path('bulkDeleteSource/', bulkDeleteSource, name='bulk_deleteSource'),

    #------------------ Ratings api Urls - ---------
    path('createRating/',createRating, name='create_ratings'),
    path('getRating/<int:RateId>/', getRating, name='get_ratings'),
    path('updateRating/<int:RateId>/',updateRating , name='update_ratings'),
    path('deleteRating/<int:RateId>/', deleteRating, name='delete_ratings'),
    path('bulkCreateRating/',bulkCreateRating,name='bulk_createRating'),
    path('bulkUpdateRating/',bulkUpdateRating,name='bulk_updateRating'),
    path('viewAllRatings/',viewAllRatings,name='view_allRatings'),
    path('bulkDeleteRating/', bulkDeleteRating, name='bulk_deleteRating'),

    #--------------------Products api urls -----------------------

    path('createProduct/',create_product),
    path('viewAllProducts/', view_all_products),
    path('updateProduct/<int:pk>/',update_product),
    path('deleteProduct/<int:pk>/',delete_product),
    path('bulkCreateProduct/',bulk_insert_products),
    path('bulkUpdateProduct/',bulk_update_products),
    path('bulkDeleteProduct/', bulk_delete_products),

    #--------------------Branch api urls -----------------------
    path('createBranch/',createBranch, name='create_Branch'),
    path('getBranch/<int:BranchId>/', getBranch, name='get_Branch'),
    path('updateBranch/<int:BranchId>/',updateBranch , name='update_Branch'),
    path('deleteBranch/<int:BranchId>/', deleteBranch, name='delete_Branch'),
    path('bulkCreateBranch/',bulkCreateBranch,name='bulk_createBranch'),
    path('viewAllBranch/',viewAllBranch,name='view_AllBranch'),
    path('bulkUpdateBranch/',bulkUpdateBranch,name='bulk_updateBranch'),
    path('bulkDeleteBranch/', bulkDeleteBranch, name='bulk_deleteBranch'),

    #--------------------Department api urls -----------------------
    path('createDepartment/',createDepartment, name='create_Department'),
    path('getDepartmentById/<int:DepartmentId>/', getDepartmentById, name='getDepartment'),
    path('updateDepartment/<int:DepartmentId>/',updateDepartment , name='update_Department'),
    path('deleteDepartment/<int:DepartmentId>/', deleteDepartment, name='delete_Department'),
    path('bulkUpdateDepartment/',bulkUpdateDepartment,name='bulk_updateDepartment'),
    path('bulkCreateDepartment/',bulkCreateDepartment,name='bulk_CreateDepartment'),
    path('bulkDeleteDepartment/', bulkDeleteDepartment, name='bulk_deleteDepartment'),
    path('viewAllDepartments/',viewAllDepartments,name='view_AllDepartments'),
   
    
    #--------------------Designation api urls -----------------------
    path('createDesignation/',createDesignation, name='create_Designation'),
    path('updateDesignation/<int:DesignationId>/',updateDesignation , name='update_Designation'),
    path('deleteDesignation/<int:DesignationId>/', deleteDesignation, name='delete_Designation'),
    path('getDesignationsById/<int:DesignationId>/',getDesignationsById),
    path('bulkCreateDesignation/',bulkCreateDesignation,name='bulk_createDesignation'),
    path('viewAllDesignations/',viewAllDesignations,name='view_AllDesignation'),
    path('bulkUpdateDesignation/',bulkUpdateDesignation,name='bulk_updateDesignation'),
    path('bulkDeleteDesignation/', bulkDeleteDesignation, name='bulk_deleteDesignation'),


    #--------------------BrokerInfo api urls -----------------------
    path('createBroker/',createBroker),

    path('get_BrokerIdentification/<int:BrokerId>/', get_BrokerIdentification),
    path('get_broker_contact_details/<int:BrokerId>/', get_broker_contact_details),
    path('get_broker_kyc_compliance/<int:BrokerId>/', get_broker_kyc_compliance),
    path('get_broker_bank_details/<int:BrokerId>/', get_broker_bank_details),
    path('get_broker_agreement/<int:BrokerId>/', get_broker_agreement),
    path('get_broker_status_audit/<int:BrokerId>/', get_broker_status_audit),
    path('update_broker/<int:BrokerId>/',update_broker),
    path('delete_broker/<int:BrokerId>/',delete_broker),
    path('getAllBrokerInfo/',getAllBrokerInfo),
    path('getBrokerInfoById/<int:id>/',getBrokerInfoById),
#     #-------------------- CustomerInfo api urls -----------------------

    path('createCustomerInfo/',createCustomerInfo),
    path('getAllCustomerInfo/', getAllCustomerInfo),   
    path('updateCustomerInfo/<int:CustomerId>/',updateCustomerInfo),
    path('deleteCustomerInfo/<int:CustomerId>/',deleteCustomerInfo),
    path('getCustomerInfoById/<int:CustomerId>/',getCustomerInfoById),
    path('bulkCreateCustomersInfo/',bulkCreateCustomersInfo),
    path('bulkDeleteCustomersInfo/',bulkDeleteCustomersInfo),   


    #--------------------Vehicle api urls -----------------------

    path('createVehicle/',createVehicle),
    path('getAllVehicles/', getAllVehicles),   
    path('updateVehicle/<int:pk>/',updateVehicle),
    path('deleteVehicle/<int:pk>/',deleteVehicle),
    path('getVehicleById/<int:pk>/',getVehicleById),
    
# #-------------------InitiateSeizure api ----------------- 

    path('createSeizure/',createSeizure),
    path('getAllSeizures/', getAllSeizures),   
    path('updateSeizure/<int:Id>/',updateSeizure),
    path('deleteSeizure/<int:Id>/',deleteSeizure),
    path('getSeizureById/<int:Id>/',getSeizureById),

# #-------------------  AssignAgent   api ----------------- 

    path('createAssignAgent/',createAssignAgent),
    path('getAllAssignAgent/', getAllAssignAgent),   
    path('updateAssignAgent/<int:Id>/',updateAssignAgent),
    path('deleteAssignAgent/<int:Id>/',deleteAssignAgent),
    path('getAssignAgentById/<int:Id>/',getAssignAgentById),


# #------------ SeizureExecution-------------------------------
    path('createSeizureExecution/',createSeizureExecution),
    path('getAllSeizureExecution/', getAllSeizureExecution),   
    path('updateSeizureExecution/<int:Id>/',updateSeizureExecution),
    path('deleteSeizureExecution/<int:Id>/',deleteSeizureExecution),
    path('getSeizureExecutionById/<int:Id>/',getSeizureExecutionById),


# #------------ AssignBrokers-------------------------------
    path('createAssignBroker/',createAssignBroker),
    path('getAllAssignBrokers/', getAllAssignBrokers),   
    path('updateAssignBroker/<int:Id>/',updateAssignBroker),
    path('deleteAssignBroker/<int:Id>/',deleteAssignBroker),
    path('getAssignBrokerById/<int:Id>/',getAssignBrokerById),

# #------------ SaleExecution-------------------------------
    path('createSaleExecution/',createSaleExecution),
    path('getAllSaleExecutions/', getAllSaleExecutions),   
    path('updateSaleExecution/<int:Id>/',updateSaleExecution),
    path('deleteSaleExecution/<int:Id>/',deleteSaleExecution),
    path('getSaleExecutionById/<int:Id>/',getSaleExecutionById),

# #------------ RecoveryClosure-------------------------------
    path('createRecoveryClosure/',createRecoveryClosure),
    path('getAllRecoveryClosures/', getAllRecoveryClosures),   
    path('updateRecoveryClosure/<int:Id>/',updateRecoveryClosure),
    path('deleteRecoveryClosure/<int:Id>/',deleteRecoveryClosure),
    path('getRecoveryClosureById/<int:Id>/',getRecoveryClosureById),

    #-------------CollateralApi----------------------------
    path('createCollateral/',createCollateral),
    path('getAllCollateral/',getAllCollateral),
    path('getCollateralById/<int:CollateralId>/',getCollateralById),
    path('updateCollateral/<int:CollateralId>/',updateCollateral),
    path('deleteCollateral/<int:CollateralId>/',deleteCollateral),
    #-------------LoanProductApi----------------------------
    path('LoanProduct/',LoanProductListCreate),
    path('LoanProductDetail/<int:pk>/',LoanProductDetail),

    #-------------interest_config ----------------------------
    path('createInterestConfig/',create_interest_config),
    path('listInterestConfigs/',list_interest_configs),
    path('getInterestConfigById/<int:ProductId>/',get_interest_config_by_product),
    path('updateInterestConfig/<int:id>/',update_interest_config),
    path('deleteInterestConfig/<int:ProductId>/',delete_interest_config),
    #-------------calculate_emi ----------------------------
    path('calculate_emi/',calculate_emi),
    #-------------calculate_emi ----------------------------
    path('createCharge/',createCharge),
    path('getAllCharges/',getAllCharges),
    path('getChargeById/<int:id>/',getChargeById),
    path('updateCharge/<int:id>/',updateCharge),
    path('deleteCharge/<int:id>/',deleteCharge),
    #-------------Penalty_emi ----------------------------
    path('createPenalty/',createPenalty),
    path('listPenalties/',listPenalties),
    path('getPenaltyById/<int:pk>/',getPenaltyById),
    path('updatePenalty/<int:pk>/',updatePenalty),
    path('deletePenalty/<int:pk>/',deletePenalty),

    #------------ TenureAmount----------------------
    path('createTenureAmount/',createTenureAmount),
    path('getTenureAmountById/<int:pk>/',getTenureAmountById),
    path('listTenureAmounts/',listTenureAmounts),
    path('updateTenureAmount/<int:pk>/',updateTenureAmount),
    path('deleteTenureAmount/<int:pk>/',deleteTenureAmount),
    #------------ BusinessRule----------------------
    path('createBusinessRule/',createBusinessRule),
    path('getBusinessRuleById/<int:pk>/',getBusinessRuleById),
    path('listBusinessRules/',listBusinessRules),
    path('updateBusinessRule/<int:pk>/',updateBusinessRule),
    path('deleteBusinessRule/<int:pk>/',deleteBusinessRule),


    path('createUDF_Mapping/',createUDF_Mapping),
    path('updateUDF_Mapping/<int:pk>/',updateUDF_Mapping),
    path('listUDF_Mapping/',listUDF_Mapping),
    path('getUDF_MappingById/<int:pk>/',getUDF_MappingById),
    path('deleteUDF_Mapping/<int:pk>/',deleteUDF_Mapping),

    path('get_all_countries/',get_all_countries),
    path('get_all_currencies/',get_all_currencies),
    # path('emi_calculator/',emi_calculator),
    path('save_emi_schedule/',save_emi_schedule),
    path('emi_calculator/',loan_emi_calculator),
    path('createLoanMasters/',createLoanMasters),


]
