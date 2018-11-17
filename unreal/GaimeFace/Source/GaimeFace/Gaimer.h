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

	FGameDetails() 
		: num_plays(0)
	{

	}
};


USTRUCT(BlueprintType)
struct FPlayReaction
{
	GENERATED_USTRUCT_BODY()

	UPROPERTY()
	int32 emotion_label;

	FPlayReaction()
		: emotion_label(0)
	{

	}
};


UCLASS()
class GAIMEFACE_API AGaimer : public ACharacter
{
	GENERATED_BODY()

private:
	FHttpModule* mHttp;
	FString mApiBaseUrl;


	TSharedRef<IHttpRequest> CreateRequest(FString SubApi);

	void ResetGame();

	void EndGame();

	FGameDetails mGameBeingWatched;
	bool mGameBegun;
	bool mEndGame;
	int32 mRemainingPlays;

	FPlayReaction mCurrentReaction;

public:
	// Sets default values for this character's properties
	AGaimer();

protected:
	// Called when the game starts or when spawned
	virtual void BeginPlay() override;


	UFUNCTION(BlueprintCallable, Meta=(Category="Script Calls"))
	void RequestStartGame(FString name);

public:	
	// Called every frame
	virtual void Tick(float DeltaTime) override;

	// Called to bind functionality to input
	virtual void SetupPlayerInputComponent(class UInputComponent* PlayerInputComponent) override;

	UFUNCTION()
	void ConsumePlay();

	void OnGameStarted(FHttpRequestPtr Request, FHttpResponsePtr Response, bool bWasSuccessful);
	void OnPlayConsumed(FHttpRequestPtr Request, FHttpResponsePtr Response, bool bWasSuccessful);

	template <typename StructType>
	void GetJsonStringFromStruct(StructType FilledStruct, FString& StringOutput);

	template <typename StructType>
	void GetStructFromJsonString(FHttpResponsePtr Response, StructType& StructOutput);

	UFUNCTION(BlueprintCallable)
	FPlayReaction GetCurrentReaction() { return mCurrentReaction; }
};
