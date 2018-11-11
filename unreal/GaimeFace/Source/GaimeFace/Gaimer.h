// Fill out your copyright notice in the Description page of Project Settings.

#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Character.h"
#include "Runtime/Online/HTTP/Public/Http.h"
#include "Json.h"
#include "JsonUtilities/Public/JsonUtilities.h"
#include "Gaimer.generated.h"

USTRUCT()
struct FGameDetails
{
	GENERATED_USTRUCT_BODY()

	UPROPERTY()
	int32 num_plays;
};


UCLASS()
class GAIMEFACE_API AGaimer : public ACharacter
{
	GENERATED_BODY()

private:
	FGameDetails mGameBeingWatched;

	FHttpModule* mHtto;
	FString mApiBaseUrl = "http://127.0.0.1:5000/";

	void SendInitRequest();

	TSharedRef<IHttpRequest> CreateRequest(FString SubApi);

public:
	// Sets default values for this character's properties
	AGaimer();

protected:
	// Called when the game starts or when spawned
	virtual void BeginPlay() override;

public:	
	// Called every frame
	virtual void Tick(float DeltaTime) override;

	// Called to bind functionality to input
	virtual void SetupPlayerInputComponent(class UInputComponent* PlayerInputComponent) override;


	void OnInitComplete(FHttpRequestPtr Request, FHttpResponsePtr Response, bool bWasSuccessful);
	void OnResponse(FHttpRequestPtr Request, FHttpResponsePtr Response, bool bWasSuccessful);

	template <typename StructType>
	void GetJsonStringFromStruct(StructType FilledStruct, FString& StringOutput);

	template <typename StructType>
	void GetStructFromJsonString(FHttpResponsePtr Response, StructType& StructOutput);
};
